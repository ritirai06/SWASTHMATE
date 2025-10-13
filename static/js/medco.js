document.addEventListener('DOMContentLoaded', function () {
  const uploadBtn = document.getElementById('upload-btn');
  const fileInput = document.getElementById('file-input');
  const progressTracker = document.getElementById('progress-tracker');
  const progressSteps = document.querySelectorAll('.progress-steps .step');
  const progressStatus = document.getElementById('progress-status');
  const analysisView = document.getElementById('analysis-view');
  const diagnosisView = document.getElementById('diagnosis-view');
  const analysisContent = document.getElementById('analysis-content');
  const diagnosisContent = document.getElementById('diagnosis-content');
  const viewReportBtn = document.getElementById('view-report-btn');
  const printBtn = document.getElementById('print-btn');
  const backBtn = document.getElementById('back-btn');

  // Step 1: Trigger file input on button click
  uploadBtn.addEventListener('click', () => fileInput.click());

  // Step 2: On file selected
  fileInput.addEventListener('change', function () {
    const file = fileInput.files[0];
    if (!file) return;

    // Show progress UI
    progressTracker.classList.remove('hidden');
    updateStep(0, 'Uploading your report...');

    const formData = new FormData();
    formData.append('report', file);

    fetch('/upload', {
      method: 'POST',
      body: formData
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status !== 'success') {
          alert('Upload failed: ' + data.message);
          return;
        }

        // Step 2: Processing
        updateStep(1, 'Processing with OCR and NLP...');

        setTimeout(() => {
          updateStep(2, 'Analyzing medical data...');

          setTimeout(() => {
            updateStep(3, 'Generating results...');
            displayResults(data);
          }, 1000);
        }, 1000);
      })
      .catch((err) => {
        console.error('Error:', err);
        alert('Something went wrong while processing the file.');
      });
  });

  function updateStep(index, statusText) {
    progressSteps.forEach((step, i) => {
      step.classList.toggle('actived', i <= index);
    });
    progressStatus.innerText = statusText;
  }

  function displayResults(data) {
  progressStatus.innerText = 'Done!';
  analysisView.style.display = 'block';

  // Summary (as-is)
  analysisContent.innerHTML = `
    <p><strong>Filename:</strong> ${data.filename}</p>
    <p><strong>Detected Diseases:</strong> ${data.analysis.diseases.join(', ') || 'None'}</p>
    <p><strong>Suggested Specialization:</strong> ${data.analysis.specialization || 'N/A'}</p>
    <p><strong>Top Recommendations:</strong><br>
      <ul>${data.recommendations.map(r => `<li>${r}</li>`).join('')}</ul>
    </p>
  `;

  // 👉 Measurements ko table me dikhaye
  const measurementsTable = `
    <h4>📊 Lab Measurements</h4>
    <table border="1" cellpadding="8" cellspacing="0" style="width:100%; border-collapse: collapse;">
      <thead>
        <tr>
          <th>Test</th>
          <th>Value</th>
          <th>Unit</th>
        </tr>
      </thead>
      <tbody>
        ${Object.entries(data.analysis.measurements || {}).map(([test, values]) =>
          (values || []).map(v => `
            <tr>
              <td>${test}</td>
              <td>${(v && v.value) !== undefined ? v.value : "-"}</td>
              <td>${(v && v.unit) ? v.unit : "-"}</td>
            </tr>
          `).join('')
        ).join('')}
      </tbody>
    </table>
  `;

  diagnosisContent.innerHTML = `
    ${measurementsTable}

    <h4>🦠 Predicted Diseases</h4>
    <ul>${(data.analysis.diseases || []).map(d => `<li>${d}</li>`).join('')}</ul>

    <h4>👨‍⚕️  Suggested Specialization</h4>
    <p>${data.analysis.specialization || 'N/A'}</p>

    <h4>📋 Recommendations</h4>
    <ul>${(data.recommendations || []).map(r => `<li>${r}</li>`).join('')}</ul>
  `;

  // (optional) Debug dekhne ke liye:
  console.log('MEASUREMENTS:', data.analysis.measurements);
}


  // View full report
  viewReportBtn.addEventListener('click', () => {
    diagnosisView.style.display = 'block';
    analysisView.style.display = 'none';
  });

  // Back to summary
  backBtn.addEventListener('click', () => {
    diagnosisView.style.display = 'none';
    analysisView.style.display = 'block';
  });

  // Print report
  printBtn.addEventListener('click', () => {
  const printContents = diagnosisContent.innerHTML;

  const printWindow = window.open('', '', 'height=800,width=1000');
  printWindow.document.write(`
    <html>
      <head>
        <title>Diagnosis Report</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            padding: 30px;
            line-height: 1.6;
            color: #333;
          }
          h2, h3 {
            color: #2c3e50;
          }
          ul {
            margin-left: 20px;
          }
        </style>
      </head>
      <body>
        <h2>🧾 Full Diagnosis Report</h2>
        ${printContents}
      </body>
    </html>
  `);

  printWindow.document.close(); // Finish loading
  printWindow.focus(); // Focus on the new window
  printWindow.print(); // Trigger print
  printWindow.close(); // Close after printing
});

});

// Contact Form Functionality
function setupContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const nameInput = document.getElementById('name');
        const emailInput = document.getElementById('email');
        const queryInput = document.getElementById('query');
        
        if (!nameInput || !emailInput || !queryInput) return;
        
        // Get the form values
        const name = nameInput.value;
        const email = emailInput.value;
        const query = queryInput.value;
        
        // Simple validation
        if (!name || !email || !query) {
            alert('Please fill out all fields');
            return;
        }
        
        // Simulate form submission
        alert(`Thank you for contacting us, ${name}! We'll get back to you soon.`);
        
        // Reset the form
        contactForm.reset();
    });
}



// contact page 
// Contact form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    
    // Add event listener to the contact form
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Get form data
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const query = document.getElementById('query').value;
            
            // Form validation
            if (!name || !email || !query) {
                showNotification('Please fill in all fields', 'error');
                return;
            }
            
            // Email validation
            if (!isValidEmail(email)) {
                showNotification('Please enter a valid email address', 'error');
                return;
            }
            
            // Prepare data to send
            const formData = {
                name: name,
                email: email,
                query: query,
                timestamp: new Date().toISOString()
            };
            
            // Show loading state
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.innerHTML = 'Sending...';
            submitButton.disabled = true;
            
            // Send data to server endpoint
            sendToDatabase(formData)
                .then(response => {
                    // Reset form
                    contactForm.reset();
                    
                    // Show success message
                    showNotification('Your message has been sent successfully!', 'success');
                })
                .catch(error => {
                    // Show error message
                    showNotification('Failed to send your message. Please try again later.', 'error');
                    console.error('Error submitting form:', error);
                })
                .finally(() => {
                    // Reset button state
                    submitButton.innerHTML = originalButtonText;
                    submitButton.disabled = false;
                });
        });
    }
    
    // Function to send data to database via API endpoint
    async function sendToDatabase(data) {
        const apiEndpoint = '/api/contact'; // This endpoint would be set up in your backend server
        
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    // Function to validate email format
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});


  

