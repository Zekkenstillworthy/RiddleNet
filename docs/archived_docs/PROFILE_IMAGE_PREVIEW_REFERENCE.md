# Profile Image Preview Implementation Reference

This document provides a simplified reference implementation for profile image preview functionality that can be used throughout the RiddleNet application.

## Basic HTML Structure

```html
<div class="profile-image-container">
    <img id="profile-img-preview" 
         src="{{ current_user.profile_image or '/static/img/default-avatar.png' }}" 
         alt="Profile Preview" 
         class="profile-image" />
    
    <input type="file" 
           id="profile-image-upload" 
           name="profile_image" 
           accept="image/*" 
           onchange="previewImage(event)" 
           style="display: none;" />
    
    <button type="button" 
            onclick="document.getElementById('profile-image-upload').click()" 
            class="upload-btn">
        📷 Change Photo
    </button>
</div>
```

## Basic CSS Styling

```css
.profile-image-container {
    position: relative;
    text-align: center;
    margin: 20px 0;
}

.profile-image {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #00d9ff;
    transition: all 0.3s ease;
}

.profile-image.loading {
    opacity: 0.6;
    filter: blur(2px);
}

.profile-image.updated {
    animation: pulse 0.6s ease-in-out;
    border-color: #00ff88;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.upload-btn {
    margin-top: 10px;
    padding: 8px 16px;
    background: #00d9ff;
    color: #000;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: bold;
}

.upload-btn:hover {
    background: #00b8d4;
}
```

## Simple JavaScript Implementation

```javascript
function previewImage(event) {
    const file = event.target.files[0];
    const preview = document.getElementById('profile-img-preview');
    
    if (!file) {
        return;
    }
    
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
    if (!allowedTypes.includes(file.type)) {
        alert('Please select a valid image file (PNG, JPG, JPEG, or GIF)');
        event.target.value = '';
        return;
    }
    
    // Validate file size (5MB limit)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size must be less than 5MB');
        event.target.value = '';
        return;
    }
    
    // Add loading state
    preview.classList.add('loading');
    
    // Create FileReader to read the selected image
    const reader = new FileReader();
    reader.onload = function(e) {
        // Update preview image with selected file
        preview.src = e.target.result;
        
        // Remove loading and add updated animation
        preview.classList.remove('loading');
        preview.classList.add('updated');
        
        // Remove animation class after it completes
        setTimeout(() => {
            preview.classList.remove('updated');
        }, 600);
    };
    
    reader.onerror = function() {
        alert('Error reading file. Please try again.');
        event.target.value = '';
        preview.classList.remove('loading');
    };
    
    // Read the file as data URL
    reader.readAsDataURL(file);
}
```

## Advanced Features (Current Implementation)

The current RiddleNet profile page includes these enhanced features:

### 1. Visual Feedback
- Loading blur effect during file processing
- Pulse animation when preview updates
- Green border and "NEW" badge when image is changed
- Notification popups for user feedback

### 2. Validation
- File type validation (PNG, JPG, JPEG, GIF)
- File size validation (5MB limit)
- Error handling with clear messages

### 3. Persistence
- Preview remains until form submission
- "Image changed" indicator persists
- Form validation integration

### 4. Accessibility
- Proper ARIA labels
- Keyboard navigation support
- Screen reader friendly

## Usage in Other Components

To implement this in other parts of the application:

1. Copy the basic HTML structure
2. Include the CSS styles
3. Add the JavaScript function
4. Customize styling to match your component's theme
5. Adjust validation rules as needed

## Backend Integration

Make sure your Flask route handles the uploaded file:

```python
@app.route('/profile', methods=['POST'])
def update_profile():
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename:
            # Process and save the file
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Update user profile with new image path
```

## Testing

Test the functionality by:
1. Selecting valid image files (PNG, JPG, JPEG, GIF)
2. Testing file size limits
3. Verifying preview updates immediately
4. Checking form submission includes the new image
5. Testing error cases (invalid files, oversized files)

This reference provides a solid foundation for implementing profile image preview functionality throughout the RiddleNet application.
