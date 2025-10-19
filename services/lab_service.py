"""
Lab Service: CRUD for labs, topology/IP config, export/import with SHA-256, deadlines, and scoring.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import hashlib

from __init__ import db
from instructor.models.lab import Lab, LabTopology, LabDevice, LabIPConfig, LabSubmission, LabDeadline, ExportHash
from instructor.models.rubric import Rubric, RubricCriterion


class LabService:
    @staticmethod
    def create_lab(owner_instructor_id: int, title: str, description: str = None, class_id: int = None, rubric_id: int = None) -> Lab:
        lab = Lab(title=title, description=description, owner_instructor_id=owner_instructor_id, class_id=class_id, rubric_id=rubric_id)
        db.session.add(lab)
        db.session.commit()
        return lab

    @staticmethod
    def upsert_topology(lab_id: int, initial_config: Dict[str, Any] = None, expected_config: Dict[str, Any] = None, validations: Dict[str, Any] = None) -> LabTopology:
        topo = LabTopology.query.filter_by(lab_id=lab_id).first()
        if not topo:
            topo = LabTopology(lab_id=lab_id)
            db.session.add(topo)
        topo.initial_config_json = json.dumps(initial_config or {})
        topo.expected_config_json = json.dumps(expected_config or {})
        topo.validations_json = json.dumps(validations or {})
        db.session.commit()
        return topo

    @staticmethod
    def add_device(lab_id: int, name: str, device_type: str) -> LabDevice:
        topo = LabTopology.query.filter_by(lab_id=lab_id).first()
        if not topo:
            topo = LabService.upsert_topology(lab_id)
        device = LabDevice(topology_id=topo.id, name=name, device_type=device_type)
        db.session.add(device)
        db.session.commit()
        return device

    @staticmethod
    def set_ip_config(device_id: int, interface: str, ip_address: str, subnet_mask: str, gateway: str = None, valid: bool = True) -> LabIPConfig:
        ipcfg = LabIPConfig(device_id=device_id, interface=interface, ip_address=ip_address, subnet_mask=subnet_mask, gateway=gateway, valid=valid)
        db.session.add(ipcfg)
        db.session.commit()
        return ipcfg

    @staticmethod
    def set_deadline(lab_id: int, due_date: datetime, late_allowed_until: Optional[datetime] = None, late_penalty_per_day: float = 10.0) -> LabDeadline:
        d = LabDeadline.query.filter_by(lab_id=lab_id).first()
        if not d:
            d = LabDeadline(lab_id=lab_id)
            db.session.add(d)
        d.due_date = due_date
        d.late_allowed_until = late_allowed_until
        d.late_penalty_per_day = late_penalty_per_day
        db.session.commit()
        return d

    @staticmethod
    def export_lab(lab_id: int, include_submissions: bool = True, created_by: Optional[int] = None) -> Dict[str, Any]:
        lab = Lab.query.get_or_404(lab_id)
        data: Dict[str, Any] = {
            'lab': lab.to_dict(),
            'topology': None,
            'devices': [],
            'ip_configs': [],
            'submissions': [],
            'rubric': None,
        }
        topo = LabTopology.query.filter_by(lab_id=lab_id).first()
        if topo:
            data['topology'] = {
                'initial_config': json.loads(topo.initial_config_json or '{}'),
                'expected_config': json.loads(topo.expected_config_json or '{}'),
                'validations': json.loads(topo.validations_json or '{}'),
            }
            for dev in topo.devices:
                data['devices'].append({'id': dev.id, 'name': dev.name, 'device_type': dev.device_type})
                for ip in dev.ip_configs:
                    data['ip_configs'].append({
                        'device_id': dev.id,
                        'interface': ip.interface,
                        'ip_address': ip.ip_address,
                        'subnet_mask': ip.subnet_mask,
                        'gateway': ip.gateway,
                        'valid': ip.valid,
                    })
        if include_submissions:
            subs = LabSubmission.query.filter_by(lab_id=lab_id).all()
            for s in subs:
                data['submissions'].append({
                    'student_id': s.student_id,
                    'submitted_at': s.submitted_at.isoformat() if s.submitted_at else None,
                    'data': json.loads(s.data_json or '{}'),
                    'score': s.score,
                    'feedback': s.feedback,
                    'rubric_breakdown': json.loads(s.rubric_breakdown_json or '{}'),
                    'status': s.status,
                })
        if lab.rubric_id:
            rub = Rubric.query.get(lab.rubric_id)
            if rub:
                data['rubric'] = rub.to_dict(include_criteria=True)
        payload = json.dumps(data, sort_keys=True).encode('utf-8')
        sha = hashlib.sha256(payload).hexdigest()
        fname = f"lab_{lab_id}_{int(datetime.utcnow().timestamp())}.json"
        eh = ExportHash(lab_id=lab_id, export_type='lab', sha256=sha, file_name=fname, created_by=created_by)
        db.session.add(eh)
        db.session.commit()
        return {'file_name': fname, 'sha256': sha, 'data': data}

    @staticmethod
    def import_lab(data: Dict[str, Any], expected_sha256: str) -> Lab:
        payload = json.dumps(data, sort_keys=True).encode('utf-8')
        sha = hashlib.sha256(payload).hexdigest()
        if sha != expected_sha256:
            raise ValueError('Integrity check failed: SHA-256 mismatch')
        lab_info = data.get('lab') or {}
        lab = Lab(
            title=lab_info.get('title', 'Imported Lab'),
            description=lab_info.get('description'),
            owner_instructor_id=lab_info.get('owner_instructor_id'),
            class_id=lab_info.get('class_id'),
            rubric_id=lab_info.get('rubric_id')
        )
        db.session.add(lab)
        db.session.flush()
        topo_data = (data.get('topology') or {})
        LabService.upsert_topology(
            lab.id,
            topo_data.get('initial_config'),
            topo_data.get('expected_config'),
            topo_data.get('validations')
        )
        # audit log import
        eh = ExportHash(
            lab_id=lab.id,
            export_type='import',
            sha256=sha,
            file_name=f"import_{lab.id}_{int(datetime.utcnow().timestamp())}.json"
        )
        db.session.add(eh)
        db.session.commit()
        return lab

    @staticmethod
    def score_submission_with_rubric(submission: LabSubmission, rubric: Rubric, criterion_scores: Dict[int, float], feedback: str = None) -> Dict[str, Any]:
        total = 0.0
        breakdown = {}
        max_total = 0.0
        for c in rubric.criteria:
            awarded = float(criterion_scores.get(c.id, 0.0))
            awarded = max(0.0, min(awarded, c.max_points))
            weighted = awarded * (c.weight or 1.0)
            breakdown[c.id] = {'title': c.title, 'awarded': awarded, 'weight': c.weight, 'weighted': weighted, 'max_points': c.max_points}
            total += weighted
            max_total += (c.max_points or 0.0) * (c.weight or 1.0)
        submission.score = total
        submission.feedback = feedback
        submission.rubric_breakdown_json = json.dumps({'criteria': breakdown, 'max_total': max_total})
        submission.status = 'graded'
        db.session.commit()
        return {'score': total, 'max_total': max_total, 'breakdown': breakdown}

    @staticmethod
    def validate_topology(lab_id: int, submission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform simple topology validation: device presence and IP formats."""
        errors: List[str] = []
        warnings: List[str] = []
        topo = LabTopology.query.filter_by(lab_id=lab_id).first()
        expected = {}
        if topo and topo.expected_config_json:
            try:
                expected = json.loads(topo.expected_config_json)
            except Exception:
                pass
        # Check device counts
        exp_devices = {d.get('name'): d for d in (expected.get('devices') or [])}
        got_devices = {d.get('name'): d for d in (submission_data.get('devices') or [])}
        for name in exp_devices.keys():
            if name not in got_devices:
                errors.append(f"Missing device: {name}")
        # Simple IP validation
        def valid_ip(ip: str) -> bool:
            try:
                parts = [int(p) for p in ip.split('.')]
                return len(parts) == 4 and all(0 <= p <= 255 for p in parts)
            except Exception:
                return False
        for dev in submission_data.get('devices', []):
            for iface in dev.get('interfaces', []):
                ip = iface.get('ip')
                mask = iface.get('mask')
                if ip and not valid_ip(ip):
                    errors.append(f"Invalid IP {ip} on {dev.get('name')}:{iface.get('name')}")
                if mask and not valid_ip(mask):
                    errors.append(f"Invalid mask {mask} on {dev.get('name')}:{iface.get('name')}")
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}
