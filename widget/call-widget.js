

//javascript
// widget/call-widget.js
(function() {
    // Configuration
    const defaultConfig = {
        serverUrl: window.location.origin,
        position: 'bottom-right',
        buttonColor: '#6366f1',
        buttonText: 'Get a Call',
        widgetTitle: 'AI call assistant'
    };

    // Create and inject CSS
    function injectStyles() {
        const styleTag = document.createElement('link');
        styleTag.rel = 'stylesheet';
        styleTag.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
        document.head.appendChild(styleTag);
        
        const fontTag = document.createElement('link');
        fontTag.rel = 'stylesheet';
        fontTag.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap';
        document.head.appendChild(fontTag);
        
        const widgetStyles = document.createElement('link');
        widgetStyles.rel = 'stylesheet';
        widgetStyles.href = `${config.serverUrl}/widget/styles.css`;
        document.head.appendChild(widgetStyles);
    }

    // Create widget DOM
    function createWidget(config) {
        // Container
        const container = document.createElement('div');
        container.id = 'lk-call-widget-container';
        
        // Call Button
        const callBtn = document.createElement('div');
        callBtn.className = 'lk-floating-call-btn';
        callBtn.id = 'lkCallBtn';
        callBtn.innerHTML = '<i class="fas fa-phone"></i>';
        
        // Form Container
        const formContainer = document.createElement('div');
        formContainer.className = 'lk-form-container';
        formContainer.id = 'lkFormContainer';
        
        // Form Header
        const formHeader = document.createElement('div');
        formHeader.className = 'lk-form-header';
        formHeader.innerHTML = `
            <h4>${config.widgetTitle}</h4>
            <span class="lk-close-btn" id="lkCloseBtn">
                <i class="fas fa-times"></i>
            </span>
        `;
        
        // Form Body
        const formBody = document.createElement('div');
        formBody.className = 'lk-form-body';
        formBody.innerHTML = `
            <form id="lkCallForm">
                <div class="lk-form-floating">
                    <label for="lkName">Full Name</label>
                    <input type="text" class="lk-form-control" id="lkName" name="name" 
                           placeholder="Enter your full name" required>
                </div>
                
                <div class="lk-form-floating">
                    <label for="lkPhone">Phone Number</label>
                    <input type="tel" class="lk-form-control" id="lkPhone" name="phone" 
                           placeholder="+1 (XXX) XXX-XXXX" required>
                </div>
                
                <div class="lk-form-floating">
                    <label for="lkEmail">Email Address</label>
                    <input type="email" class="lk-form-control" id="lkEmail" name="email" 
                           placeholder="name@example.com" required>
                </div>
                
                <div class="lk-form-floating">
                    <label for="lkQuery">What would you like to discuss?</label>
                    <textarea class="lk-form-control" id="lkQuery" name="query" 
                              placeholder="Tell us about your requirements" style="height: 120px"></textarea>
                </div>
                
                <button type="submit" class="lk-btn-primary">
                    <i class="fas fa-phone"></i>
                    <span>${config.buttonText}</span>
                </button>
            </form>
            
            <div id="lkResponseMessage" class="lk-alert">
                <!-- Response message will be displayed here -->
            </div>
        `;
        
        // Assemble
        formContainer.appendChild(formHeader);
        formContainer.appendChild(formBody);
        container.appendChild(callBtn);
        container.appendChild(formContainer);
        
        return container;
    }

    // Add event listeners
    function setupEventListeners() {
        const callBtn = document.getElementById('lkCallBtn');
        const formContainer = document.getElementById('lkFormContainer');
        const closeBtn = document.getElementById('lkCloseBtn');
        const callForm = document.getElementById('lkCallForm');
        
        // Toggle form visibility
        callBtn.addEventListener('click', () => {
            formContainer.classList.add('active');
        });
        
        closeBtn.addEventListener('click', () => {
            formContainer.classList.remove('active');
        });
        
        // Form submission
        callForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="lk-spinner-border" role="status" aria-hidden="true"></span> Processing...';
            
            const formData = new FormData(this);
            
            fetch(`${config.serverUrl}/submit`, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                const responseDiv = document.getElementById('lkResponseMessage');
                
                if (data.success) {
                    responseDiv.className = "lk-alert lk-alert-success show";
                    responseDiv.innerHTML = `<strong>Success!</strong> ${data.message}`;
                    callForm.reset();
                    
                    // Auto close form after success
                    setTimeout(() => {
                        formContainer.classList.remove('active');
                    }, 3000);
                } else {
                    responseDiv.className = "lk-alert lk-alert-danger show";
                    responseDiv.innerHTML = `<strong>Error!</strong> ${data.message}`;
                }
                
                submitButton.disabled = false;
                submitButton.innerHTML = `<i class="fas fa-phone"></i><span>${config.buttonText}</span>`;
            })
            .catch(error => {
                console.error('Error:', error);
                const responseDiv = document.getElementById('lkResponseMessage');
                responseDiv.className = "lk-alert lk-alert-danger show";
                responseDiv.innerHTML = '<strong>Error!</strong> Something went wrong. Please try again later.';
                
                submitButton.disabled = false;
                submitButton.innerHTML = `<i class="fas fa-phone"></i><span>${config.buttonText}</span>`;
            });
        });
    }

    // Initialize with configuration
    function init(userConfig = {}) {
        // Merge configurations
        config = { ...defaultConfig, ...userConfig };
        
        // Inject styles
        injectStyles();
        
        // Create and inject widget
        const widget = createWidget(config);
        document.body.appendChild(widget);
        
        // Setup event listeners
        setupEventListeners();
    }

    // Expose to global scope
    window.LiveKitCallWidget = {
        init: init
    };
})();