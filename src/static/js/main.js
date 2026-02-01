// MWECAU ICT Club Attendance System - Client-side JavaScript

// API Base URL
const API_BASE = '';

// Load session information
async function loadSessionInfo() {
    try {
        const response = await fetch(`${API_BASE}/api/session-info`);
        const result = await response.json();

        const sessionInfoDiv = document.getElementById('sessionInfo');
        
        if (result.success && result.data.has_session) {
            const session = result.data.session;
            const isActive = session.attendance_window.is_active;
            
            sessionInfoDiv.className = isActive ? 'session-info session-active' : 'session-info session-inactive';
            sessionInfoDiv.innerHTML = `
                <h3>${session.day}, ${session.date}</h3>
                <p><strong>Department:</strong> ${session.department}</p>
                <p><strong>Time:</strong> ${session.time}</p>
                <p><strong>Status:</strong> ${isActive ? 'Attendance window is OPEN' : 'Attendance window is CLOSED'}</p>
                ${session.attendance_window.time_remaining ? `<p><strong>Time Remaining:</strong> ${session.attendance_window.time_remaining}</p>` : ''}
                ${!isActive && session.attendance_window.reason ? `<p><small>${session.attendance_window.reason}</small></p>` : ''}
            `;
        } else {
            sessionInfoDiv.className = 'session-info session-inactive';
            sessionInfoDiv.innerHTML = `
                <p>${result.data.message}</p>
                ${result.data.next_session ? `<p>Next session: ${result.data.next_session.date} (${result.data.next_session.department})</p>` : ''}
            `;
        }
    } catch (error) {
        console.error('Error loading session info:', error);
        const sessionInfoDiv = document.getElementById('sessionInfo');
        if (sessionInfoDiv) {
            sessionInfoDiv.innerHTML = '<p>Unable to load session information</p>';
        }
    }
}

// Show message
function showMessage(elementId, message, type = 'info') {
    const messageDiv = document.getElementById(elementId);
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    messageDiv.style.display = 'block';
}

// Hide message
function hideMessage(elementId) {
    const messageDiv = document.getElementById(elementId);
    messageDiv.style.display = 'none';
}

// Handle registration form submission
async function handleRegistration(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = document.getElementById('submitBtn');
    const messageDiv = document.getElementById('message');
    
    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registering...';
    hideMessage('message');
    
    // Get form data
    const formData = new FormData(form);
    
    // Get selected departments
    const departments = [];
    const deptCheckboxes = form.querySelectorAll('input[name="departments"]:checked');
    deptCheckboxes.forEach(cb => departments.push(cb.value));
    
    if (departments.length === 0) {
        showMessage('message', 'Please select at least one department', 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
        return;
    }
    
    // Prepare data
    const data = {
        reg_number: formData.get('reg_number').trim(),
        full_name: formData.get('full_name').trim(),
        email: formData.get('email').trim(),
        phone: formData.get('phone').trim(),
        gender: formData.get('gender'),
        year_of_study: parseInt(formData.get('year_of_study')),
        course: formData.get('course'),
        departments: departments
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('message', result.message || 'Registration successful!', 'success');
            form.reset();
            
            // Redirect to attendance page after 2 seconds
            setTimeout(() => {
                window.location.href = '/attendance';
            }, 2000);
        } else {
            let errorMsg = result.error.message;
            if (result.error.details) {
                if (typeof result.error.details === 'object') {
                    errorMsg += ': ' + Object.values(result.error.details).join(', ');
                } else {
                    errorMsg += ': ' + result.error.details;
                }
            }
            showMessage('message', errorMsg, 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showMessage('message', 'An error occurred. Please try again.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register';
    }
}

// Handle member check (Step 1)
async function handleMemberCheck(event) {
    event.preventDefault();
    
    const form = event.target;
    const checkBtn = document.getElementById('checkBtn');
    const regNumber = document.getElementById('regNumber').value.trim();
    
    // Disable button
    checkBtn.disabled = true;
    checkBtn.textContent = 'Checking...';
    hideMessage('step1Message');
    
    try {
        const response = await fetch(`${API_BASE}/api/check-member`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ reg_number: regNumber })
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.data.exists) {
                // Member exists, show step 2
                const member = result.data.member;
                document.getElementById('memberName').textContent = member.full_name;
                document.getElementById('regNumberHidden').value = regNumber;
                
                // Hide step 1, show step 2
                document.getElementById('step1').style.display = 'none';
                document.getElementById('step2').style.display = 'block';
                
                // Focus on session code input
                document.getElementById('sessionCode').focus();
            } else {
                // Member doesn't exist
                showMessage('step1Message', 
                    'Registration number not found. Please register first or check your number.', 
                    'error');
                
                // Offer to redirect to registration
                setTimeout(() => {
                    if (confirm('Would you like to register now?')) {
                        window.location.href = '/register';
                    }
                }, 1000);
            }
        } else {
            showMessage('step1Message', result.error.message, 'error');
        }
    } catch (error) {
        console.error('Check member error:', error);
        showMessage('step1Message', 'An error occurred. Please try again.', 'error');
    } finally {
        checkBtn.disabled = false;
        checkBtn.textContent = 'Continue';
    }
}

// Handle attendance marking (Step 2)
async function handleAttendance(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = document.getElementById('submitBtn');
    const regNumber = document.getElementById('regNumberHidden').value;
    const sessionCode = document.getElementById('sessionCode').value.trim();
    
    // Disable button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Marking...';
    hideMessage('step2Message');
    
    try {
        const response = await fetch(`${API_BASE}/api/mark-attendance`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reg_number: regNumber,
                session_code: sessionCode
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Hide step 2
            document.getElementById('step2').style.display = 'none';
            
            // Show success message
            const successDiv = document.getElementById('successMessage');
            document.getElementById('successName').textContent = result.data.full_name;
            document.getElementById('successDate').textContent = result.data.session_date;
            document.getElementById('successDepartment').textContent = result.data.department;
            successDiv.style.display = 'block';
            
            // Scroll to success message
            successDiv.scrollIntoView({ behavior: 'smooth' });
        } else {
            showMessage('step2Message', `${result.error.message}: ${result.error.details || ''}`, 'error');
        }
    } catch (error) {
        console.error('Mark attendance error:', error);
        showMessage('step2Message', 'An error occurred. Please try again.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Mark Attendance';
    }
}

// Reset attendance form
function resetForm() {
    document.getElementById('step1').style.display = 'block';
    document.getElementById('step2').style.display = 'none';
    document.getElementById('successMessage').style.display = 'none';
    document.getElementById('regNumber').value = '';
    document.getElementById('sessionCode').value = '';
    hideMessage('step1Message');
    hideMessage('step2Message');
    
    // Focus on registration number input
    document.getElementById('regNumber').focus();
}
