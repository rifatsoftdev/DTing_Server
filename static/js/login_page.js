
import { ApiClient } from "./ApiClient.js";
import { loginUser } from "./user_auth.js";
import { loadCountries } from "./countries.js"


const api = new ApiClient(window.location.origin);

// Global variables
let currentLoginMethod = 'email';
let isSubmitting = false;

// DOM elements
const elements = {
    emailTab: document.getElementById('method-email-tab'),
    phoneTab: document.getElementById('method-phone-tab'),
    emailForm: document.getElementById('method-email'),
    phoneForm: document.getElementById('method-phone'),
    emailInput: document.getElementById('email'),
    emailPassword: document.getElementById('email-password'),
    phoneNumber: document.getElementById('phone-number'),
    phonePassword: document.getElementById('phone-password'),
    countryCode: document.getElementById('country-code'),
    toggleEmailPassword: document.getElementById('toggleEmailPassword'),
    togglePhonePassword: document.getElementById('togglePhonePassword'),
    emailEyeIcon: document.getElementById('emailEyeIcon'),
    phoneEyeIcon: document.getElementById('phoneEyeIcon'),
    errorMessage: document.getElementById('error-message'),
    successMessage: document.getElementById('success-message'),
    loginBtn: document.getElementById('login-btn'),
    loginSpinner: document.getElementById('loginSpinner'),
    loginBtnText: document.getElementById('loginBtnText')
};

// Initialize the page
document.addEventListener('DOMContentLoaded', async function() {
    if (typeof bootstrap !== 'undefined' && bootstrap.Tab) {
        await initCountrySelector();
        setupEventListeners();
        updateSubmitState();
    } else {
        await loadBootstrapAndInit();
    }
});

// Load Bootstrap and initialize
async function loadBootstrapAndInit() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js';
    script.onload = async function() {
        await initCountrySelector();
        setupEventListeners();
        updateSubmitState();
    };
    document.head.appendChild(script);
}

// Initialize country selector
async function initCountrySelector() {
    await loadCountries(elements.countryCode);
    populateCountryDropdown();
}

// Populate country dropdown
function populateCountryDropdown() {
    if (elements.countryCode) {
        elements.countryCode.innerHTML = '<option value="" disabled selected>Select country</option>';
        window.countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country.country_code;
            option.textContent = `${country.flag_emoji} ${country.country_name} ${country.country_code}`;
            elements.countryCode.appendChild(option);
        });
    }
}

// Setup event listeners
function setupEventListeners() {
    // Tab switching
    if (elements.emailTab) {
        elements.emailTab.addEventListener('shown.bs.tab', function() {
            currentLoginMethod = 'email';
            clearAlerts();
            updateSubmitState();
        });
    }

    if (elements.phoneTab) {
        elements.phoneTab.addEventListener('shown.bs.tab', function() {
            currentLoginMethod = 'phone';
            clearAlerts();
            updateSubmitState();
        });
    }

    // Password toggle
    if (elements.toggleEmailPassword) {
        elements.toggleEmailPassword.addEventListener('click', function() {
            togglePasswordVisibility(elements.emailPassword, elements.emailEyeIcon);
        });
    }

    if (elements.togglePhonePassword) {
        elements.togglePhonePassword.addEventListener('click', function() {
            togglePasswordVisibility(elements.phonePassword, elements.phoneEyeIcon);
        });
    }

    // Input validation
    const allInputs = [
        elements.emailInput, elements.emailPassword,
        elements.phoneNumber, elements.phonePassword
    ].filter(input => input);

    allInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
            }
            updateSubmitState();
        });
    });

    if (elements.countryCode) {
        elements.countryCode.addEventListener('change', function() {
            if (this.value) {
                this.classList.remove('is-invalid');
            }
            updateSubmitState();
        });
    }
}

// Toggle password visibility
function togglePasswordVisibility(inputField, iconElement) {
    if (inputField.type === 'password') {
        inputField.type = 'text';
        iconElement.classList.remove('fa-eye');
        iconElement.classList.add('fa-eye-slash');
    } else {
        inputField.type = 'password';
        iconElement.classList.remove('fa-eye-slash');
        iconElement.classList.add('fa-eye');
    }
}

// Handle email login
async function handleEmailLogin(e) {
    e.preventDefault();
    
    if (!validateEmailForm()) return;
    if (isSubmitting) return;
    
    setLoading(true);
    clearAlerts();
    
    const email_address = elements.emailInput.value.trim();
    const password = elements.emailPassword.value;
    
    try {
        await loginUser(api, {
            email_address: email_address,
            phone_number: null,
            country_code: null,
            user_password: password
        });
    } catch (error) {
        showError(error.message || 'Login failed. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Handle phone login
async function handlePhoneLogin(e) {
    e.preventDefault();
    
    if (!validatePhoneForm()) return;
    if (isSubmitting) return;
    
    setLoading(true);
    clearAlerts();
    
    const country_code = elements.countryCode.value;
    const phone_number = elements.phoneNumber.value;
    const password = elements.phonePassword.value;
    
    try {
        await loginUser(api, {
            email_address: null,
            phone_number: phone_number,
            country_code: country_code,
            user_password: password
        });
    } catch (error) {
        showError(error.message || 'Login failed. Please try again.');
    } finally {
        setLoading(false);
    }
}

// Validate email form
function validateEmailForm() {
    let isValid = true;
    
    if (!elements.emailInput.value.trim()) {
        showFieldError(elements.emailInput, 'Please enter your email address.');
        isValid = false;
    } else if (!isValidEmail(elements.emailInput.value)) {
        showFieldError(elements.emailInput, 'Please enter a valid email address.');
        isValid = false;
    } else {
        elements.emailInput.classList.add('is-valid');
    }
    
    if (!elements.emailPassword.value) {
        showFieldError(elements.emailPassword, 'Please enter your password.');
        isValid = false;
    } else {
        elements.emailPassword.classList.add('is-valid');
    }
    
    if (isValid) {
        elements.emailForm.classList.add('was-validated');
    }
    
    return isValid;
}

// Validate phone form
function validatePhoneForm() {
    let isValid = true;
    
    if (!elements.countryCode.value) {
        showFieldError(elements.countryCode, 'Please select a country code.');
        isValid = false;
    } else {
        elements.countryCode.classList.add('is-valid');
    }
    
    if (!elements.phoneNumber.value) {
        showFieldError(elements.phoneNumber, 'Please enter your phone number.');
        isValid = false;
    } else if (!isValidPhone(elements.phoneNumber.value)) {
        showFieldError(elements.phoneNumber, 'Please enter a valid phone number.');
        isValid = false;
    } else {
        elements.phoneNumber.classList.add('is-valid');
    }
    
    if (!elements.phonePassword.value) {
        showFieldError(elements.phonePassword, 'Please enter your password.');
        isValid = false;
    } else {
        elements.phonePassword.classList.add('is-valid');
    }
    
    if (isValid) {
        elements.phoneForm.classList.add('was-validated');
    }
    
    return isValid;
}

// Show field error
function showFieldError(inputElement, message) {
    inputElement.classList.add('is-invalid');
    inputElement.classList.remove('is-valid');
    
    let errorElement = inputElement.nextElementSibling;
    if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        inputElement.parentNode.appendChild(errorElement);
    }
    errorElement.textContent = message;
}

// Validate email
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Validate phone
function isValidPhone(phone) {
    return /^[+]?\d{10,15}$/.test(phone.replace(/\s/g, ''));
}

// Set loading state
function setLoading(isLoading) {
    isSubmitting = isLoading;
    elements.loginBtn.disabled = !isLoading ? !validateCurrentForm() : true;
    
    const spinner = document.getElementById('loginSpinner') || document.createElement('span');
    if (!spinner.id) {
        spinner.id = 'loginSpinner';
        spinner.className = 'spinner-border spinner-border-sm d-none me-2';
        elements.loginBtn.insertBefore(spinner, elements.loginBtn.firstChild);
    }
    
    spinner.classList.toggle('d-none', !isLoading);
    
    if (elements.loginBtnText) {
        elements.loginBtnText.textContent = isLoading ? 'Signing In...' : 'Sign In';
    }
    elements.loginBtn.classList.toggle('loading', isLoading);
}

// Update submit state based on form validity
function updateSubmitState() {
    const isValid = validateCurrentForm();
    if (elements.loginBtn) {
        elements.loginBtn.disabled = !isValid || isSubmitting;
    }
}

// Validate current form based on active tab
function validateCurrentForm() {
    if (currentLoginMethod === 'email') {
        return elements.emailInput.value.trim() && 
                elements.emailPassword.value && 
                isValidEmail(elements.emailInput.value);
    } else {
        return elements.countryCode.value && 
                elements.phoneNumber.value && 
                elements.phonePassword.value &&
                isValidPhone(elements.phoneNumber.value);
    }
}

// Clear alerts
function clearAlerts() {
    if (elements.errorMessage) {
        elements.errorMessage.classList.add('d-none');
        elements.errorMessage.textContent = '';
    }
    if (elements.successMessage) {
        elements.successMessage.classList.add('d-none');
        elements.successMessage.textContent = '';
    }
    
    document.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
        el.classList.remove('is-invalid', 'is-valid');
    });
}

// Show error message
function showError(message) {
    clearAlerts();
    if (elements.errorMessage) {
        elements.errorMessage.textContent = message;
        elements.errorMessage.classList.remove('d-none');
    }
}

// Show success message
function showSuccess(message) {
    clearAlerts();
    if (elements.successMessage) {
        elements.successMessage.textContent = message;
        elements.successMessage.classList.remove('d-none');
    }
}

// Google Sign Up (mock implementation)
function googleSignUp() {
    if (isSubmitting) return;
    
    setLoading(true);
    showSuccess('Google sign-in initiated. Redirecting to Google...');
    
    setTimeout(() => {
        window.location.href = '/dashboard.html';
    }, 1500);
}

// Facebook Sign Up (mock implementation)
function facebookSignUp() {
    if (isSubmitting) return;
    
    setLoading(true);
    showSuccess('Facebook sign-in initiated. Redirecting to Facebook...');
    
    setTimeout(() => {
        window.location.href = '/dashboard.html';
    }, 1500);
}

// Real-time validation
[elements.emailInput, elements.emailPassword, elements.phoneNumber, elements.phonePassword].forEach(input => {
    if (input) {
        input.addEventListener('keyup', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
            }
            updateSubmitState();
        });
    }
});

if (elements.countryCode) {
    elements.countryCode.addEventListener('change', function() {
        if (this.checkValidity()) {
            this.classList.remove('is-invalid');
        }
        updateSubmitState();
    });
}

// Form submit handler
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', function(e) {
        if (currentLoginMethod === 'email') {
            handleEmailLogin(e);
        } else {
            handlePhoneLogin(e);
        }
    });
}
