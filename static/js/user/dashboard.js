// Dashboard and navigation logic migrated from script.js

document.addEventListener('DOMContentLoaded', function() {
    
    // Global event delegation for all submission buttons (essay, fill-in-blank, short answer)
    document.body.addEventListener('click', function(event) {
        // Handle essay submission button
        const submitEssayBtn = event.target.closest('.submit-essay-btn');
        if (submitEssayBtn) {
            const essayInput = document.querySelector('.essay-input');
            if (essayInput) {
                const userInput = essayInput.value;
                
                // Show loading state
                const originalText = submitEssayBtn.innerHTML;
                submitEssayBtn.innerHTML = '<span class="loading-dots"></span>';
                submitEssayBtn.disabled = true;
                
                // Process submission after a short delay to show animation
                setTimeout(() => {
                    window.handleEssaySubmission(userInput);
                    // Reset button
                    submitEssayBtn.innerHTML = originalText;
                    submitEssayBtn.disabled = false;
                }, 800);
            }
        }
        
        // Handle fill-in-blank submission button
        const submitBlankBtn = event.target.closest('.submit-blank-btn');
        if (submitBlankBtn) {
            console.log('Fill-in-blank submit button clicked via delegation');
            const blankInput = document.querySelector('.blank-input');
            if (blankInput) {
                const userInput = blankInput.value;
                if (window.checkBlankAnswer) {
                    window.checkBlankAnswer(userInput);
                } else {
                    console.error('checkBlankAnswer function not available');
                }
            }
        }
        
        // Handle short answer submission button
        const submitShortAnswerBtn = event.target.closest('.submit-short-answer-btn');
        if (submitShortAnswerBtn) {
            console.log('Short answer submit button clicked via delegation');
            const shortAnswerInput = document.querySelector('.short-answer-input');
            if (shortAnswerInput) {
                const userInput = shortAnswerInput.value;
                if (window.checkShortAnswer) {
                    window.checkShortAnswer(userInput);
                } else {
                    console.error('checkShortAnswer function not available');
                }
            }
        }
    });
    
    // Section/blur logic
    const header = document.querySelector('.header');
    const sections = document.querySelectorAll('section');
    const navlinks = document.querySelectorAll('header nav a');
    const profileLink = document.querySelector('.profile-link');
    const profileExitBtn = document.querySelector('.profile-exit-btn');
    const profile = document.querySelector('#profile');

    // Intersection Observer to highlight nav links on scroll
    const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5
    };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id || 'dashboard';
                navlinks.forEach(link => {
                    link.classList.remove('active');
                    const href = link.getAttribute('href').replace('#', '');
                    if ((href === '' && id === 'dashboard') || href === id) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, options);
    sections.forEach(section => observer.observe(section));

    // Smooth scrolling for nav links
    document.querySelectorAll('.navbar a').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = link.getAttribute('href');
            if (href === '/logout' || (href.startsWith('/') && href !== '#')) return;
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                const targetSection = document.querySelector(targetId);
                if (targetSection) targetSection.scrollIntoView({ behavior: 'smooth' });
            }
            document.querySelectorAll('.navbar a').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Show/hide profile section
    if (profileLink && profileExitBtn && profile) {
        profileLink.onclick = () => {
            profile.classList.add('active');
            sections.forEach(section => {
                if (section !== profile) {
                    section.classList.add('blur');
                    header.classList.add('blur');
                }
            });
            document.body.style.overflow = 'hidden';
        };
        profileExitBtn.onclick = () => {
            profile.classList.remove('active');
            sections.forEach(section => section.classList.remove('blur'));
            header.classList.remove('blur');
            document.body.style.overflow = '';
        };
    }

    // Classes popup and class details logic migrated from classes-popup.js and class-details.js

    // Classes popup logic
    const classesLink = document.getElementById('classes-link');
    const choiceClassesBtn = document.getElementById('choice-classes-btn');
    const classesPopup = document.getElementById('classes-popup');
    const classesExitBtn = document.querySelector('.classes-exit-btn');
    const classesExitIcon = document.querySelector('.bx.bx-x.classes-exit-btn');
    const joinClassForm = document.getElementById('join-class-form');
    const classCodeInput = document.getElementById('class-code');
    const errorAlert = document.getElementById('error-alert');
    const successAlert = document.getElementById('success-alert');
    const joinSpinner = document.getElementById('join-spinner');
    const classesContainer = document.getElementById('classes-container');
    const classTemplate = document.getElementById('class-template');
    const emptyStateTemplate = document.getElementById('empty-state-template');

    function showClassesPopup() {
        classesPopup.classList.add('active');
        sections.forEach(section => {
            if (section !== classesPopup) {
                section.classList.add('blur');
                header.classList.add('blur');
            }
        });
        document.body.style.overflow = 'hidden';
        const exitButton = document.querySelector('.classes-exit-btn');
        if (exitButton) {
            exitButton.onclick = function() {
                hideClassesPopup();
                return false;
            };
        }
        loadEnrolledClasses();
    }
    function hideClassesPopup() {
        classesPopup.classList.remove('active');
        sections.forEach(section => section.classList.remove('blur'));
        header.classList.remove('blur');
        document.body.style.overflow = '';
    }
    if (classesLink) {
        classesLink.addEventListener('click', function(e) {
            e.preventDefault();
            showClassesPopup();
        });
    }
    if (choiceClassesBtn) {
        choiceClassesBtn.addEventListener('click', function() {
            const popupInfo = document.querySelector('.popup-info');
            if (popupInfo) {
                popupInfo.classList.remove('active');
                sections.forEach(section => section.classList.remove('blur'));
                header.classList.remove('blur');
            }
            showClassesPopup();
        });
    }
    if (classesExitBtn) {
        classesExitBtn.addEventListener('click', function(e) {
            e.preventDefault();
            hideClassesPopup();
        });
    }
    if (classesExitIcon) {
        classesExitIcon.addEventListener('click', function(e) {
            e.preventDefault();
            hideClassesPopup();
        });
    }
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('classes-exit-btn') || event.target.classList.contains('bx-x')) {
            hideClassesPopup();
        }
    });
    if (joinClassForm) {
        joinClassForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const classCode = classCodeInput.value.trim();
            if (!classCode || classCode.length !== 6) {
                showError('Please enter a valid 6-character class code');
                return;
            }
            hideAlerts();
            joinSpinner.style.display = 'inline-block';
            fetch('/api/join-class', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: classCode })
            })
            .then(response => response.json())
            .then(data => {
                joinSpinner.style.display = 'none';
                if (data.status === 'error') {
                    showError(data.message || 'Failed to join class');
                    return;
                }
                showSuccess(data.message || 'Successfully joined the class!');
                classCodeInput.value = '';
                loadEnrolledClasses();
            })
            .catch(error => {
                joinSpinner.style.display = 'none';
                showError('An error occurred. Please try again.');
                console.error('Error:', error);
            });
        });
    }
    function showError(message) {
        if (errorAlert) {
            errorAlert.textContent = message;
            errorAlert.style.display = 'block';
            successAlert.style.display = 'none';
        }
    }
    function showSuccess(message) {
        if (successAlert) {
            successAlert.textContent = message;
            successAlert.style.display = 'block';
            errorAlert.style.display = 'none';
        }
    }
    function hideAlerts() {
        if (errorAlert) errorAlert.style.display = 'none';
        if (successAlert) successAlert.style.display = 'none';
    }
    function loadEnrolledClasses() {
        if (!classesContainer) return;
        classesContainer.innerHTML = `<div class="loading" style="text-align: center; padding: 1rem;"><div class="spinner" style="display: inline-block; width: 30px; height: 30px;"></div><p>Loading your classes...</p></div>`;
        fetch('/api/classes')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                classesContainer.innerHTML = `<p class="error">${data.message || 'Failed to load classes'}</p>`;
                return;
            }
            if (!data.classes || data.classes.length === 0) {
                classesContainer.innerHTML = '';
                const emptyState = document.importNode(emptyStateTemplate.content, true);
                classesContainer.appendChild(emptyState);
                return;
            }
            const classesGrid = document.createElement('div');
            classesGrid.className = 'classes-grid';
            data.classes.forEach(classItem => {
                const classCard = document.importNode(classTemplate.content, true);
                classCard.querySelector('.class-name').textContent = classItem.name;
                classCard.querySelector('.class-section').textContent = classItem.section || '';
                classCard.querySelector('.class-description').textContent = classItem.description || 'No description available';
                classCard.querySelector('.start-date').textContent = `Start: ${formatDate(classItem.startDate)}`;
                classCard.querySelector('.end-date').textContent = `End: ${formatDate(classItem.endDate)}`;
                classCard.querySelector('.student-count').textContent = `Students: ${classItem.studentCount || 0}`;
                const viewBtn = classCard.querySelector('.view-class-btn');
                viewBtn.href = '#';
                viewBtn.setAttribute('data-class-id', classItem.id);
                const leaveBtn = classCard.querySelector('.leave-class-btn');
                leaveBtn.setAttribute('data-class-id', classItem.id);
                leaveBtn.setAttribute('data-class-name', classItem.name);
                classesGrid.appendChild(classCard);
            });
            classesContainer.innerHTML = '';
            classesContainer.appendChild(classesGrid);
            document.querySelectorAll('.view-class-btn').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    const classId = this.getAttribute('data-class-id');
                    if (classId && window.showClassDetailsPopup) {
                        window.showClassDetailsPopup(classId);
                    }
                });
            });
            document.querySelectorAll('.info-btn').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    const classCard = this.closest('.class-card');
                    if (classCard) {
                        const viewBtn = classCard.querySelector('.view-class-btn');
                        const classId = viewBtn.getAttribute('data-class-id');
                        if (classId && window.showClassDetailsPopup) {
                            window.showClassDetailsPopup(classId);
                        }
                    }
                });
            });
            document.querySelectorAll('.leave-class-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const classId = this.getAttribute('data-class-id');
                    const className = this.getAttribute('data-class-name');
                    if (confirm(`Are you sure you want to leave ${className}? This action cannot be undone.`)) {
                        leaveClass(classId);
                    }
                });
            });
        })
        .catch(error => {
            classesContainer.innerHTML = `<p class="error">Failed to load classes. Please try again later.</p>`;
            console.error('Error:', error);
        });
    }
    function leaveClass(classId) {
        if (!classId) return;
        fetch(`/api/leave-class/${classId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                showError(data.message || 'Failed to leave class');
                return;
            }
            showSuccess(data.message || 'Successfully left the class!');
            loadEnrolledClasses();
        })
        .catch(error => {
            showError('An error occurred. Please try again.');
            console.error('Error:', error);
        });
    }
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return dateString;
        return date.toLocaleDateString();
    }
    window.showClassesPopup = showClassesPopup;
    window.hideClassesPopup = hideClassesPopup;
    window.loadEnrolledClasses = loadEnrolledClasses;

    // Class details popup logic (from user/class-details.js)
    const classDetailsPopup = document.createElement('div');
    classDetailsPopup.id = 'class-details-popup';
    classDetailsPopup.className = 'popup';
    document.body.appendChild(classDetailsPopup);
    classDetailsPopup.innerHTML = `
        <div class="popup-content">
            <div class="popup-header">
                <h3 class="class-title">Class Details</h3>
                <button class="close-btn class-details-exit-btn"><i class="fas fa-times"></i></button>
            </div>
            <div class="popup-body" id="class-details-content">
                <div class="class-info-container">
                    <div class="spinner-border text-primary" role="status" id="class-details-loading">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div id="class-details-data" style="display: none;">
                        <div class="class-detail-item"><span class="detail-label">Class Name:</span><span class="detail-value" id="class-name-details"></span></div>
                        <div class="class-detail-item"><span class="detail-label">Section:</span><span class="detail-value" id="class-section-details"></span></div>
                        <div class="class-detail-item"><span class="detail-label">Description:</span><p class="detail-value" id="class-description-details"></p></div>
                        <div class="class-detail-item"><span class="detail-label">Start Date:</span><span class="detail-value" id="class-start-date-details"></span></div>
                        <div class="class-detail-item"><span class="detail-label">End Date:</span><span class="detail-value" id="class-end-date-details"></span></div>
                        <div class="class-detail-item"><span class="detail-label">Enrollment Count:</span><span class="detail-value" id="class-enrollment-details"></span></div>
                        <div class="class-detail-item"><span class="detail-label">Class Code:</span><span class="detail-value" id="class-code-details"></span></div>
                    </div>
                    <div id="class-details-error" style="display: none;"><p class="error-message">Failed to load class details. Please try again.</p></div>
                </div>
            </div>
        </div>
    `;
    classDetailsPopup.addEventListener('click', function(event) {
        const target = event.target.closest('.class-details-exit-btn');
        if (target) hideClassDetailsPopup();
    });
    window.addEventListener('click', function(event) {
        if (event.target === classDetailsPopup) hideClassDetailsPopup();
    });
    window.showClassDetailsPopup = function(classId) {
        const clickSound = document.getElementById('clickSound');
        if (clickSound) {
            clickSound.currentTime = 0;
            clickSound.play().catch(e => console.log('Sound play prevented:', e));
        }
        const loadingElement = document.getElementById('class-details-loading');
        const dataElement = document.getElementById('class-details-data');
        const errorElement = document.getElementById('class-details-error');
        if (loadingElement) loadingElement.style.display = 'block';
        if (dataElement) dataElement.style.display = 'none';
        if (errorElement) errorElement.style.display = 'none';
        classDetailsPopup.classList.add('active');
        document.querySelectorAll('section').forEach(section => {
            if (section.id !== 'class-details-popup') section.classList.add('blur');
        });
        document.querySelector('.header').classList.add('blur');
        document.body.style.overflow = 'hidden';
        fetch(`/api/class/${classId}`)
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch class details');
            return response.json();
        })
        .then(classData => {
            if (classData.status === 'error') throw new Error(classData.message || 'Failed to fetch class details');
            document.getElementById('class-name-details').textContent = classData.name;
            document.getElementById('class-section-details').textContent = classData.section || 'N/A';
            document.getElementById('class-description-details').textContent = classData.description || 'No description available';
            document.getElementById('class-start-date-details').textContent = formatDate(classData.start_date);
            document.getElementById('class-end-date-details').textContent = formatDate(classData.end_date);
            document.getElementById('class-enrollment-details').textContent = classData.enrollment_count || '0';
            document.getElementById('class-code-details').textContent = classData.code;
            if (loadingElement) loadingElement.style.display = 'none';
            if (dataElement) dataElement.style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching class details:', error);
            if (loadingElement) loadingElement.style.display = 'none';
            if (errorElement) {
                errorElement.style.display = 'block';
                const errorMessage = document.querySelector('#class-details-error .error-message');
                if (errorMessage) errorMessage.textContent = error.message || 'Failed to load class details. Please try again.';
            }
        });
    };
    function hideClassDetailsPopup() {
        classDetailsPopup.classList.remove('active');
        document.querySelectorAll('section').forEach(section => section.classList.remove('blur'));
        document.querySelector('.header').classList.remove('blur');
        document.body.style.overflow = 'auto';
        const navSound = document.getElementById('navSound');
        if (navSound) {
            navSound.currentTime = 0;
            navSound.play().catch(e => console.log('Sound play prevented:', e));
        }
    }
    window.hideClassDetailsPopup = hideClassDetailsPopup;

    // Quiz/Riddle functionality migrated from script.js
    let questionCount = 0;  
    let questionNumb = 1;
    let userScore = 0;
    let questions = []; // Will be populated from API

    // Start RiddleNet Button const
    const startBtn = document.querySelector('.start-btn');
    const popupInfo = document.querySelector('.popup-info');
    const exitBtn = document.querySelector('.exit-btn');
    const main = document.querySelector('#dashboard');
    
    // Topology riddle Button
    const continueBtn = document.querySelector('.continue-btn');
    const quizSection = document.querySelector('.quiz-section');
    const quizBox = document.querySelector('.quiz-box');
    const nextBtn = document.querySelector('.next-btn');   
    const optionList = document.querySelector('.option-list');
    const resultBox = document.querySelector('.result-box');
    const tryAgainBtn = document.querySelector('.tryAgain-btn')
    const goHomeQuizBtn = document.querySelector('.goHome-quiz-btn'); 
    const goHomeResultBtn = document.querySelector('.goHome-result-btn'); 
    const topologySound = document.getElementById('bgSound');
    const homeSection = document.querySelector('.home');

    // Exit button functionality
    if (startBtn && popupInfo) {
        startBtn.onclick = () => {
            // Reset state variables
            questionCount = 0;  
            questionNumb = 1;
            userScore = 0;
            popupInfo.classList.add('active');
            document.querySelectorAll('section').forEach(section => {
                if (section.id !== 'profile') {
                    section.classList.add('blur'); 
                    document.querySelector('.header').classList.add('blur'); 
                }
            });
            document.body.style.overflow = 'hidden';
        };
    }

    if (exitBtn && popupInfo) {
        exitBtn.onclick = () => {
            popupInfo.classList.remove('active');
            document.querySelectorAll('section').forEach(section => {
                section.classList.remove('blur');
            });
            document.querySelector('.header').classList.remove('blur');
            document.body.style.overflow = '';
        };
    }

    // Fetch questions from API
    async function fetchQuestions(category = 'riddle') {
        try {
            console.log(`Attempting to fetch ${category} questions from database...`);
            
            // Try the main API endpoint first
            let response = await fetch(`/api/questions?category=${category}`);
            
            // If that fails, try the direct QuizController endpoint
            if (!response.ok) {
                console.warn(`Main API endpoint failed with ${response.status}, trying alternate endpoint...`);
                response = await fetch(`/questions?category=${category}`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch questions from all endpoints: ${response.status} ${response.statusText}`);
                }
            }
            
            const data = await response.json();
            questions = data;
            
            console.log(`Successfully loaded ${questions.length} questions from database`);
            console.log('First question:', questions.length > 0 ? questions[0] : 'No questions found');
            
            return questions.length > 0;
        } catch (error) {
            console.error('Error fetching questions from database:', error);
            alert('Failed to load questions. Please contact an administrator or check browser console for details.');
            return false;
        }
    }

    // Continue button functionality
    if (continueBtn) {
        continueBtn.onclick = async () => {
            // Reset state variables
            questionCount = 0;  
            questionNumb = 1;
            userScore = 0;
            
            // Show loading indicator
            const loadingIndicator = document.createElement('div');
            loadingIndicator.textContent = "Loading questions...";
            loadingIndicator.style.color = "#fff";
            loadingIndicator.style.textAlign = "center";
            loadingIndicator.style.marginTop = "20px";
            if (popupInfo) popupInfo.appendChild(loadingIndicator);
            
            // Fetch questions from the database before starting the quiz
            const questionsLoaded = await fetchQuestions('riddle');
            
            // Remove loading indicator
            if (popupInfo) popupInfo.removeChild(loadingIndicator);
            
            if (!questionsLoaded) {
                alert('No questions available in the database. Please try again later or contact an administrator to add questions.');
                return;
            }
            
            if (quizSection) quizSection.classList.add('active');
            if (popupInfo) popupInfo.classList.remove('active');
            if (main) main.classList.remove('active');
            if (quizBox) quizBox.classList.add('active');
    
            if (popupInfo) popupInfo.classList.remove('active');
            document.querySelectorAll('section').forEach(section => {
                section.classList.remove('blur');
            });
            document.querySelector('.header').classList.remove('blur'); 
            document.body.style.overflow = 'none';
            showQuestions(0);
            questionCounter(1);
            headerScore();
        };
    }

    // Try again button functionality
    if (tryAgainBtn) {
        tryAgainBtn.onclick = () => {
            // First make sure both are visible before changing their state
            if (resultBox) resultBox.style.display = 'none';
            if (quizBox) quizBox.style.display = 'block';
    
            // Now add/remove active classes
            if (quizBox) quizBox.classList.add('active');
            if (resultBox) resultBox.classList.remove('active');
            if (nextBtn) nextBtn.classList.remove('active');
    
            // Reset quiz state
            questionCount = 0;  
            questionNumb = 1;
            userScore = 0;
            
            // Load the first question and update displays
            showQuestions(questionCount);
            questionCounter(questionNumb);
            headerScore();
        };
    }

    // Go home from quiz button functionality
    if (goHomeQuizBtn) {
        goHomeQuizBtn.onclick = () => {
            // Reset quiz state
            questionCount = 0;  
            questionNumb = 1;
            userScore = 0;
    
            setTimeout(() => {
                location.reload();
            }, 100);
            
            // Pause background sound first
            if (topologySound) {
                topologySound.pause();
                topologySound.currentTime = 0;
                topologySound.loop = false;
            }
    
            document.body.style.overflow = '';
            if (quizSection) quizSection.classList.remove('active');
            if (quizBox) quizBox.classList.remove('active');
            if (nextBtn) nextBtn.classList.remove('active');
            if (homeSection) homeSection.classList.add('active');
        };
    }

    // Go home from results button functionality
    if (goHomeResultBtn) {
        goHomeResultBtn.onclick = () => {
            if (topologySound) {
                topologySound.pause();
                topologySound.currentTime = 0;
                topologySound.loop = false;
            }
    
            setTimeout(() => {
                location.reload();
            }, 100);
            document.body.style.overflow = '';
            if (resultBox) resultBox.classList.remove('active');
            if (quizSection) quizSection.classList.remove('active');
            if (quizBox) quizBox.classList.remove('active');
            if (nextBtn) nextBtn.classList.remove('active');
            if (homeSection) homeSection.classList.add('active');
            
            // Reset quiz state
            questionCount = 0;
            questionNumb = 1;
            userScore = 0;
            
            // Update display
            headerScore();
            
            // Reset the next button
            if (nextBtn) nextBtn.classList.remove('active');
        };
    }

    // Next button functionality
    if (nextBtn) {
        nextBtn.onclick = () => {
            if (questionCount < questions.length - 1){
                questionCount++;
                showQuestions(questionCount);
                questionNumb++;
                questionCounter(questionNumb);
    
                nextBtn.classList.remove('active');
            } else {
                console.log("All questions answered, showing result box");
                showResultBox();
            }
        };
    }

    // Function to show questions
    function showQuestions(index) {
        if (!questions || questions.length === 0) {
            console.error('No questions loaded from database');
            return;
        }
    
        const questionText = document.querySelector('.question-text');
        if (!questionText) return;
        
        questionText.textContent = `${questions[index].numb}. ${questions[index].question}`;
    
        // Get question type from explanation field
        const questionExplanation = questions[index].explanation || '';
        const isBlankQuestion = questionExplanation.includes('[TYPE:fill_blank]');
        const isShortAnswerQuestion = questionExplanation.includes('[TYPE:short_answer]');
        const isMatchingQuestion = questionExplanation.includes('[TYPE:matching]');
        const isEssayQuestion = questionExplanation.includes('[TYPE:essay]');
        
        // Update the quiz header to display the question type
        const quizHeaderSpan = document.querySelector('.quiz-header span:first-child');
        if (!quizHeaderSpan) return;
        
        let questionType = 'Multiple Choice';
        
        if (isBlankQuestion) {
            questionType = 'Fill in the Blank';
        } else if (isShortAnswerQuestion) {
            questionType = 'Short Answer';
        } else if (isMatchingQuestion) {
            questionType = 'Drag & Drop Matching';
        } else if (isEssayQuestion) {
            questionType = 'Essay Question';
        } else if (questions[index].options && questions[index].options.length === 2 && 
                  (questions[index].options[0].includes('True') || questions[index].options[0].includes('False'))) {
            questionType = 'True/False';
        }
        
        // Update the header with the question type and category
        const category = window.location.pathname.includes('topology') ? 'Topology' : 
                        window.location.pathname.includes('troubleshoot') ? 'Troubleshooting' : 
                        window.location.pathname.includes('crimp') ? 'Cable Crimping' : 'Riddle';
        
        quizHeaderSpan.textContent = `${questionType} ${category}`;
        
        // Clear previous content
        if (optionList) optionList.innerHTML = '';
        
        // Hide all special question containers
        const matchingContainer = document.querySelector('.matching-container');
        const essayContainer = document.querySelector('.essay-container');
        if (matchingContainer) matchingContainer.style.display = 'none';
        if (essayContainer) essayContainer.style.display = 'none';
        
        if (isBlankQuestion) {
            // Handle fill in the blank questions
            handleFillInBlankQuestion();
        } else if (isShortAnswerQuestion) {
            // Handle short answer questions
            handleShortAnswerQuestion();
        } else if (isMatchingQuestion) {
            // Handle matching questions 
            if (typeof createDragDropMatchingInterface === 'function') {
                createDragDropMatchingInterface(questions[index]);
            } else {
                console.error('createDragDropMatchingInterface function not found');
            }
        } else if (isEssayQuestion) {
            // Handle essay questions
            handleEssayQuestion();
        } else {
            // Standard multiple choice question
            handleMultipleChoiceQuestion(index);
        }
    }

    // Mock handler functions that would need to be implemented
    function handleFillInBlankQuestion() {
        // Implementation for fill in blank questions
        if (!optionList) return;
        
        // Clear any previous content
        optionList.innerHTML = '';
        
        const inputField = document.createElement('div');
        inputField.className = 'blank-input-container';
        inputField.innerHTML = `
            <input type="text" class="blank-input" placeholder="Type your answer here...">
            <button type="button" class="submit-blank-btn">Submit</button>
        `;
        optionList.appendChild(inputField);
        
        // Add event listener for the submit button
        const submitBtn = document.querySelector('.submit-blank-btn');
        if (submitBtn) {
            // Remove any existing event listeners by cloning the node
            const newSubmitBtn = submitBtn.cloneNode(true);
            submitBtn.parentNode.replaceChild(newSubmitBtn, submitBtn);
            
            // Add event listener to the new button
            newSubmitBtn.addEventListener('click', function() {
                console.log('Fill-in-blank submit button clicked via direct handler');
                const userInput = document.querySelector('.blank-input').value;
                if (typeof window.checkBlankAnswer === 'function') {
                    window.checkBlankAnswer(userInput);
                } else {
                    console.error('checkBlankAnswer function not available globally');
                }
            });
        }
        
        // Also allow pressing Enter to submit
        const blankInput = document.querySelector('.blank-input');
        if (blankInput) {
            blankInput.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    console.log('Enter key pressed in fill-in-blank input');
                    const userInput = blankInput.value;
                    if (typeof window.checkBlankAnswer === 'function') {
                        window.checkBlankAnswer(userInput);
                    } else {
                        console.error('checkBlankAnswer function not available globally');
                    }
                }
            });
        }
    }

    function handleShortAnswerQuestion() {
        // Implementation for short answer questions
        if (!optionList) return;
        
        // Clear any previous content
        optionList.innerHTML = '';
        
        const inputField = document.createElement('div');
        inputField.className = 'short-answer-container';
        inputField.innerHTML = `
            <textarea class="short-answer-input" placeholder="Enter your answer here..." rows="4"></textarea>
            <p class="character-count">0 characters</p>
            <button type="button" class="submit-short-answer-btn">Submit</button>
        `;
        optionList.appendChild(inputField);
        
        // Add character count functionality
        const textArea = document.querySelector('.short-answer-input');
        const charCount = document.querySelector('.character-count');
        if (textArea && charCount) {
            textArea.addEventListener('input', function() {
                const count = this.value.length;
                charCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
            });
        }
        
        // Add event listener for the submit button
        const submitBtn = document.querySelector('.submit-short-answer-btn');
        if (submitBtn && textArea) {
            // Remove any existing event listeners by cloning the node
            const newSubmitBtn = submitBtn.cloneNode(true);
            submitBtn.parentNode.replaceChild(newSubmitBtn, submitBtn);
            
            // Add event listener to the new button
            newSubmitBtn.addEventListener('click', function() {
                console.log('Short answer submit button clicked via direct handler');
                const userInput = textArea.value;
                if (typeof window.checkShortAnswer === 'function') {
                    window.checkShortAnswer(userInput);
                } else {
                    console.error('checkShortAnswer function not available globally');
                }
            });
        }
        
        // Also allow pressing Ctrl+Enter to submit
        if (textArea) {
            textArea.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && event.ctrlKey) {
                    event.preventDefault();
                    console.log('Ctrl+Enter pressed in short answer input');
                    const userInput = textArea.value;
                    if (typeof window.checkShortAnswer === 'function') {
                        window.checkShortAnswer(userInput);
                    } else {
                        console.error('checkShortAnswer function not available globally');
                    }
                }
            });
        }
    }

    function handleEssayQuestion() {
        // Implementation for essay questions
        const essayContainer = document.querySelector('.essay-container');
        if (!essayContainer) return;
        
        essayContainer.style.display = 'block';
        
        // Reset essay input
        const essayInput = document.querySelector('.essay-input');
        if (essayInput) essayInput.value = '';
        
        // Reset character count
        const charCount = document.querySelector('.character-count');
        const countNumberElement = document.querySelector('.count-number');
        if (countNumberElement) {
            countNumberElement.textContent = '0';
        } else if (charCount) {
            charCount.innerHTML = '<span class="count-number">0</span> characters';
        }
        
        // Reset feedback area
        const feedbackArea = document.querySelector('.essay-feedback');
        if (feedbackArea) {
            feedbackArea.innerHTML = '';
            feedbackArea.className = 'essay-feedback';
            feedbackArea.style.display = 'none';
        }
        
        // Add character count functionality with smooth animation
        if (essayInput && charCount) {
            essayInput.addEventListener('input', function() {
                const count = this.value.length;
                const countElement = document.querySelector('.count-number');
                
                // Animate the character count change
                if (countElement) {
                    // Slight scale animation on change
                    countElement.style.transition = 'transform 0.2s ease';
                    countElement.style.transform = 'scale(1.1)';
                    countElement.textContent = count;
                    
                    setTimeout(() => {
                        countElement.style.transform = 'scale(1)';
                    }, 200);
                } else if (charCount) {
                    charCount.innerHTML = `<span class="count-number">${count}</span> character${count !== 1 ? 's' : ''}`;
                }
            });
        }
        
        // Add event listener for the submit button with loading state
        const submitBtn = document.querySelector('.submit-essay-btn');
        if (submitBtn && essayInput) {
            // Remove any existing event listeners
            submitBtn.replaceWith(submitBtn.cloneNode(true));
            
            // Get the fresh reference
            const freshSubmitBtn = document.querySelector('.submit-essay-btn');
            
            // Add event listener
            freshSubmitBtn.addEventListener('click', function() {
                const userInput = essayInput.value;
                
                // Show loading state
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="loading-dots"></span>';
                this.disabled = true;
                
                // Process submission after a short delay to show animation
                setTimeout(() => {
                    handleEssaySubmission(userInput);
                    // Reset button
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 800);
            });
            
            console.log('Essay submit button event listener attached');
        }
        
        // Also allow pressing Ctrl+Enter to submit
        if (essayInput && submitBtn) {
            essayInput.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && event.ctrlKey) {
                    event.preventDefault();
                    const userInput = this.value;
                    
                    // Show loading state on button
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<span class="loading-dots"></span>';
                    submitBtn.disabled = true;
                    
                    // Process submission
                    setTimeout(() => {
                        handleEssaySubmission(userInput);
                        // Reset button
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }, 800);
                }
            });
        }
    }

    function handleMultipleChoiceQuestion(index) {
        // Implementation for multiple choice questions
        if (!optionList || !questions[index].options) return;
        
        let optionHTML = '';
        questions[index].options.forEach((option, i) => {
            optionHTML += `
                <div class="option">
                    <span>${option}</span>
                </div>
            `;
        });
        
        optionList.innerHTML = optionHTML;
        
        const options = optionList.querySelectorAll('.option');
        options.forEach((option, i) => {
            option.onclick = function() {
                window.optionSelected(this, index);
            };
        });
    }

    // Function to handle essay submissions
    function handleEssaySubmission(userInput) {
        if (!userInput || userInput.trim().length < 10) {
            alert('Please provide a more detailed answer before submitting.');
            return false;
        }
        
        // Get the current question data
        const currentQuestion = questions[questionCount];
        
        console.log("Submitting essay response:", userInput.substring(0, 50) + "...");
        
        // Show a feedback message
        const feedbackArea = document.querySelector('.essay-feedback');
        if (!feedbackArea) return false;
        
        feedbackArea.style.display = 'block';
        feedbackArea.innerHTML = `
            <div class="feedback-message">
                <p><strong>Your response has been submitted.</strong></p>
                <p>Your essay will be reviewed by an instructor.</p>
            </div>
        `;
        feedbackArea.className = 'essay-feedback success';
        
        // Add option to view grading criteria or model answer if available
        if (currentQuestion && (currentQuestion.model_answer || currentQuestion.rubric)) {
            feedbackArea.innerHTML += `
                <button class="show-guidance-btn">View Guidance</button>
            `;
            
            document.querySelector('.show-guidance-btn').addEventListener('click', () => {
                if (typeof showEssayGuidance === 'function') {
                    showEssayGuidance(currentQuestion);
                }
            });
        }
        
        // Save the response to the server
        if (currentQuestion) {
            fetch('/save_essay', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: currentQuestion.id,
                    questionId: currentQuestion.id,
                    question: currentQuestion.question,
                    answer: userInput,
                    category: window.location.pathname.includes('topology') ? 'topology' : 
                             window.location.pathname.includes('troubleshoot') ? 'troubleshoot' : 
                             window.location.pathname.includes('crimp') ? 'crimping' : 'riddle'
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Essay saved successfully:", data);
                // Keep the success message as is
            })
            .catch(error => {
                console.error("Error saving essay:", error);
                feedbackArea.innerHTML = `
                    <div class="feedback-message error">
                        <p><strong>Warning:</strong> There was an error saving your response.</p>
                        <p>Please try again later or contact support.</p>
                    </div>
                `;
                feedbackArea.className = 'essay-feedback error';
            });
        }
        
        // Disable the text area and submit button to prevent multiple submissions
        const essayInput = document.querySelector('.essay-input');
        if (essayInput) essayInput.disabled = true;
        
        const submitEssayBtn = document.querySelector('.submit-essay-btn');
        if (submitEssayBtn) submitEssayBtn.disabled = true;
        
        // Enable the next button
        if (nextBtn) nextBtn.classList.add('active');
        
        // For scoring purposes, we'll give a nominal score for essay completion
        // This would be updated later when the essay is actually graded
        userScore += 0.5;  // Give half a point for submitting
        headerScore();
        
        // Play a sound for submission
        if (typeof playCorrectSound === 'function') {
            playCorrectSound();
        }
        
        return true;
    }

    // Function to show essay guidance (model answer or rubric)
    function showEssayGuidance(question) {
        const feedbackArea = document.querySelector('.essay-feedback');
        if (!feedbackArea) return;
        
        let guidanceContent = '';
        
        if (question.rubric) {
            guidanceContent += `
                <div class="essay-guidance-section">
                    <h4>Grading Rubric:</h4>
                    <p>${question.rubric}</p>
                </div>
            `;
        }
        
        if (question.model_answer) {
            guidanceContent += `
                <div class="essay-guidance-section">
                    <h4>Sample Answer:</h4>
                    <p>${question.model_answer}</p>
                </div>
            `;
        }
        
        if (!guidanceContent) {
            guidanceContent = '<p>No additional guidance is available for this question.</p>';
        }
        
        feedbackArea.innerHTML = `
            <div class="feedback-message">
                <h3>Essay Guidance</h3>
                ${guidanceContent}
                <button class="close-guidance-btn">Close</button>
            </div>
        `;
        
        document.querySelector('.close-guidance-btn').addEventListener('click', () => {
            // Restore the original feedback
            feedbackArea.innerHTML = `
                <div class="feedback-message">
                    <p><strong>Your response has been submitted.</strong></p>
                    <p>Your essay will be reviewed by an instructor.</p>
                </div>
                <button class="show-guidance-btn">View Guidance</button>
            `;
            
            document.querySelector('.show-guidance-btn').addEventListener('click', () => {
                showEssayGuidance(question);
            });
        });
    }

    // Helper functions for question display
    function questionCounter(index) {
        const questionTotal = document.querySelector('.question-total');
        if (questionTotal && questions.length) {
            questionTotal.textContent = `${index} of ${questions.length} Questions`;
        }
    }

    function headerScore() {
        const headerScoreText = document.querySelector('.header-score');
        if (headerScoreText) {
            headerScoreText.textContent = `Score: ${userScore}/${questions.length}`;
        }
    }

    function showResultBox() {
        if (!quizBox || !resultBox) return;
        
        quizBox.classList.remove('active');
        resultBox.classList.add('active');
        
        const scoreText = resultBox.querySelector('.score-text');
        if (scoreText) {
            scoreText.textContent = `Your Score: ${userScore} out of ${questions.length}`;
        }
        
        // Add to database via API
        saveScore(userScore, questions.length);
    }

    async function saveScore(score, total) {
        const scorePercent = (score / total) * 100;
        const category = window.location.pathname.includes('topology') ? 'topology' : 
                          window.location.pathname.includes('troubleshoot') ? 'troubleshoot' : 
                          window.location.pathname.includes('crimp') ? 'crimping' : 'riddle';
        
        try {
            const response = await fetch('/api/save-score', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    score: scorePercent / 100, // Convert to decimal (0.0 to 1.0)
                    category: category
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to save score');
            }
            
            const data = await response.json();
            console.log('Score saved successfully:', data);
        } catch (error) {
            console.error('Error saving score:', error);
        }
    }

    // Make these functions available globally
    window.headerScore = headerScore;
    window.questionCounter = questionCounter;
    window.showQuestions = showQuestions;
    window.showResultBox = showResultBox;
    
    // Make quiz-related functions available globally for HTML event binding
    window.handleEssaySubmission = function(userInput) {
        console.log("Global handleEssaySubmission called");
        return handleEssaySubmission(userInput);
    };
    window.showEssayGuidance = showEssayGuidance;
    
    // Define globally accessible function for option selection
    window.optionSelected = function(option, index) {
        // Handle option selection for multiple choice questions
        const allOptions = document.querySelectorAll('.option');
        
        // Check if this is the correct answer
        const correctAnswer = questions[index].answer.toLowerCase();
        const userAnswer = option.textContent.trim().toLowerCase();
        
        if (userAnswer === correctAnswer) {
            // Correct answer
            option.classList.add('correct');
            userScore++;
            headerScore();
            
            // Play correct sound if available
            if (typeof playCorrectSound === 'function') {
                playCorrectSound();
            }
        } else {
            // Wrong answer
            option.classList.add('incorrect');
            
            // Mark the correct answer
            allOptions.forEach(opt => {
                if (opt.textContent.trim().toLowerCase() === correctAnswer) {
                    opt.classList.add('correct');
                }
            });
            
            // Play incorrect sound if available
            if (typeof playIncorrectSound === 'function') {
                playIncorrectSound();
            }
        }
        
        // Disable all options
        allOptions.forEach(opt => {
            opt.classList.add('disabled');
            opt.removeAttribute('onclick');
        });
        
        // Show the next button
        if (nextBtn) {
            nextBtn.classList.add('active');
        }
    };
    
    // Implement and expose the checkBlankAnswer function
    function checkBlankAnswer(userInput) {
        if (!userInput || !userInput.trim()) {
            alert('Please enter an answer before submitting.');
            return;
        }
        
        // Get the current question data
        const currentQuestion = questions[questionCount];
        
        if (!currentQuestion) {
            console.error('No current question found for blank answer check');
            return;
        }
        
        // Remove case sensitivity and trim whitespace for comparison
        const userAnswer = userInput.trim().toLowerCase();
        const correctAnswer = currentQuestion.answer.trim().toLowerCase();
        
        // Check if the answer is correct
        const isCorrect = userAnswer === correctAnswer;
        
        // Get the input container
        const blankInputContainer = document.querySelector('.blank-input-container');
        
        if (blankInputContainer) {
            // Clear any previous feedback
            const oldFeedback = blankInputContainer.querySelector('.answer-feedback');
            if (oldFeedback) {
                blankInputContainer.removeChild(oldFeedback);
            }
            
            // Create feedback element
            const feedback = document.createElement('div');
            feedback.className = 'answer-feedback';
            
            if (isCorrect) {
                // Correct answer
                feedback.innerHTML = '<p class="correct-answer">Correct! ✓</p>';
                feedback.className += ' correct';
                userScore++;
                headerScore();
                
                // Play correct sound if available
                window.playCorrectSound();
            } else {
                // Wrong answer
                feedback.innerHTML = `
                    <p class="incorrect-answer">Incorrect ✗</p>
                    <p class="correct-answer-text">The correct answer is: ${currentQuestion.answer}</p>
                `;
                feedback.className += ' incorrect';
                
                // Play incorrect sound if available
                window.playIncorrectSound();
            }
            
            // Append feedback
            blankInputContainer.appendChild(feedback);
            
            // Disable the input and button
            const blankInput = document.querySelector('.blank-input');
            const submitBtn = document.querySelector('.submit-blank-btn');
            
            if (blankInput) blankInput.disabled = true;
            if (submitBtn) submitBtn.disabled = true;
        }
        
        // Show the next button
        if (nextBtn) {
            nextBtn.classList.add('active');
        }
    }
    
    // Implement checkShortAnswer function
    function checkShortAnswer(userInput) {
        if (!userInput || userInput.trim().length < 5) {
            alert('Please provide a more detailed answer before submitting.');
            return;
        }
        
        // Get the current question data
        const currentQuestion = questions[questionCount];
        
        if (!currentQuestion) {
            console.error('No current question found for short answer check');
            return;
        }
        
        console.log("Checking short answer submission:", userInput.substring(0, 30) + "...");
        
        // Get the short answer container
        const shortAnswerContainer = document.querySelector('.short-answer-container');
        
        if (!shortAnswerContainer) {
            console.error('Short answer container not found');
            return;
        }
        
        // Clear any previous feedback
        const oldFeedback = shortAnswerContainer.querySelector('.answer-feedback');
        if (oldFeedback) {
            shortAnswerContainer.removeChild(oldFeedback);
        }
        
        // For short answers, we'll provide general feedback since exact matching might be too strict
        const feedback = document.createElement('div');
        feedback.className = 'answer-feedback submitted';
        
        // Check for keywords in the answer to determine correctness
        const keywords = currentQuestion.answer.toLowerCase().split(/[,\s]+/).filter(word => word.length > 3);
        const userAnswerLower = userInput.toLowerCase();
        
        let keywordsFound = 0;
        keywords.forEach(keyword => {
            if (userAnswerLower.includes(keyword)) {
                keywordsFound++;
            }
        });
        
        const percentageMatch = keywords.length > 0 ? (keywordsFound / keywords.length) : 0;
        
        // Determine how "correct" the answer is based on keywords
        if (percentageMatch > 0.7) {
            // Excellent answer
            feedback.innerHTML = '<p class="correct-answer">Excellent Answer! ✓</p>';
            feedback.className += ' correct';
            userScore++;
            headerScore();
            window.playCorrectSound();
        } else if (percentageMatch > 0.4) {
            // Partially correct
            feedback.innerHTML = '<p class="partial-answer">Partially Correct</p>';
            feedback.className += ' partial';
            userScore += 0.5;
            headerScore();
            window.playCorrectSound();
        } else {
            // Insufficient answer
            feedback.innerHTML = `
                <p class="incorrect-answer">Your answer is missing key elements</p>
                <p class="sample-answer">A good answer would include: ${currentQuestion.answer}</p>
            `;
            feedback.className += ' incorrect';
            window.playIncorrectSound();
        }
        
        // Append feedback
        shortAnswerContainer.appendChild(feedback);
        
        // Disable the textarea and button
        const shortAnswerInput = document.querySelector('.short-answer-input');
        const submitBtn = document.querySelector('.submit-short-answer-btn');
        
        if (shortAnswerInput) shortAnswerInput.disabled = true;
        if (submitBtn) submitBtn.disabled = true;
        
        // Show the next button
        if (nextBtn) {
            nextBtn.classList.add('active');
        }
    }
    
    // Make functions global
    window.checkBlankAnswer = checkBlankAnswer;
    window.checkShortAnswer = checkShortAnswer;
    
    // Log that global functions are exposed
    console.log("Quiz-related global functions initialized:", {
        handleEssaySubmission: !!window.handleEssaySubmission,
        showEssayGuidance: !!window.showEssayGuidance,
        optionSelected: !!window.optionSelected,
        checkBlankAnswer: !!window.checkBlankAnswer,
        checkShortAnswer: !!window.checkShortAnswer
    });
    
    // Add sound functions
    window.playCorrectSound = function() {
        const sound = document.getElementById('correctSound');
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(e => console.log('Sound play prevented:', e));
        }
    };
    
    window.playIncorrectSound = function() {
        const sound = document.getElementById('incorrectSound');
        if (sound) {
            sound.currentTime = 0;
            sound.play().catch(e => console.log('Sound play prevented:', e));
        }
    };
});