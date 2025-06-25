// 1. Grab upload elements
const uploadBtn = document.getElementById("upload-btn");
const fileInput = document.getElementById("file-input");
const progressTracker = document.getElementById("progress-tracker");
const statusText = document.getElementById("progress-status");
const steps = document.querySelectorAll(".step");

uploadBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (!file) return;

  uploadBtn.textContent = "File Selected";
  progressTracker.classList.remove("hidden");
  statusText.textContent = "Uploading your report...";

  const formData = new FormData();
  formData.append("report", file);

  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();

    if (res.ok) {
       // Step updates
      steps.forEach((s, i) => s.classList.remove("actived"));
      steps[0].classList.add("actived"); // Upload done
      steps[1].classList.add("actived"); // Processing
      statusText.textContent = "Processing your report...";

      setTimeout(() => {
        steps[2].classList.add("actived"); // Analysis
        statusText.textContent = "Analyzing your report...";
      }, 1500);

      setTimeout(() => {
        steps[3].classList.add("actived"); // Done
        statusText.textContent = "✅ Analysis Complete!";
      }, 3000);
      window.extracted = data.extracted || {};

      // Show buttons now that analysis-view is visible
      const buttonsSection = document.querySelector('.print-download-buttons');
      if (buttonsSection) buttonsSection.style.display = 'block';

      // Display Extracted Text
      const extractedTextContainer = document.getElementById("extracted-text");
      extractedTextContainer.textContent = data.extracted_text || "No text extracted.";

      // Display Metrics
      const metricsContainer = document.getElementById("metrics");
      metricsContainer.innerHTML = ''; // Clear previous metrics
      for (const key in data.metrics) {
        const p = document.createElement("p");
        p.textContent = `${key}: ${data.metrics[key]}`;
        metricsContainer.appendChild(p);
      }

      // Display Diagnosis
      const diagnosisContainer = document.getElementById("diagnosis");
      diagnosisContainer.innerHTML = ''; // Clear previous diagnosis
      data.diagnosis.forEach(diag => {
        const p = document.createElement("p");
        p.textContent = diag;
        diagnosisContainer.appendChild(p);
      });

      // Display Recommendations
      const recommendationsContainer = document.getElementById("recommendations");
      recommendationsContainer.innerHTML = ''; // Clear previous recommendations
      data.recommendations.forEach(rec => {
        const p = document.createElement("p");
        p.textContent = rec;
        recommendationsContainer.appendChild(p);
      });

      // Switch to analysis view
      activateView('analysis-view');
    } else {
      statusText.textContent = `❌ Error: ${data.error || "Unknown error occurred."}`;
    }
  } catch (err) {
    statusText.textContent = "❌ Upload failed. Try again.";
    console.error(err);
  }
});


function populateDiagnosis(data) {
  const patientInfo = document.querySelector('.patient-info');
  if (!patientInfo) return;
  patientInfo.innerHTML = '';
  Object.keys(data).forEach(key => {
    const field = data[key];
    const item  = document.createElement('div');
    item.className = 'info-item';
    item.innerHTML = `<span class="info-label">${key}</span>
                      <span class="info-value">${field.value} ${field.unit}</span>`;
    patientInfo.appendChild(item);
  });
}

function viewDiagnosisOnly() {
  populateDiagnosis(window.extracted);
  activateView('diagnosis-view');
}

function showDiagnosisAndPrint() {
  populateDiagnosis(window.extracted);
  activateView('diagnosis-view');
  window.print();
}

function activateView(viewId) {
  [ 'upload-view','about-view', 'analysis-view', 'history-view', 'contact-view']
    .forEach(id => {
      const sec = document.getElementById(id);
      if (sec) sec.style.display = 'none';
    });
  const target = document.getElementById(viewId);
  if (target) target.style.display = 'block';

}
function activateView(viewId) {
  const views = document.querySelectorAll("main > section, section[id$='view']");
  views.forEach(view => {
    view.classList.remove("active");
  });

  const targetView = document.getElementById(viewId);
  if (targetView) {
    targetView.classList.add("active");
  }
}


           
        // 1. Extracted values ko global bana lo
        
            let extracted = { 
                "patientName": "John Doe",  // Add patient name here
                "BMI": { "unit": "kg/m2", "value": 26.3 },
                "BloodPressure": { "unit": "mmHg", "value": "12/17" },
                "Hemoglobin": { "unit": "g/dL", "value": 12 },
                "SGPT": { "unit": "U/L", "value": 97.2 }
            };
      
        // 2. Diagnosis View ko populate karne ka function
        function populateDiagnosis(data) {
          const patientInfo = document.querySelector('.patient-info');
          if (!patientInfo) return;
      
          // Optional: purana data clean karo
          patientInfo.innerHTML = '';
      
          Object.keys(data).forEach(key => {
            const field = data[key];
            const infoItem = document.createElement('div');
            infoItem.className = 'info-item';
            infoItem.innerHTML = `
              <span class="info-label">${key}</span>
              <span class="info-value">${field.value} ${field.unit}</span>
            `;
            patientInfo.appendChild(infoItem);
          });
        }
      
        // 3. Jab Analysis Complete ho:
        function onAnalysisComplete() {
          const statusText = document.getElementById('status-text');
          statusText.textContent = "✅ Analysis Complete!"; // sirf message show karna
        }
      
        // 4. Jab Print ya View Report karna ho:
        function showDiagnosisAndPrint() {
          populateDiagnosis(extracted); // Pehle Diagnosis page ka data bharo
          activateView('diagnosis-view'); // Diagnosis view ko show karo
          window.print(); // print popup lao
        }
      
        // 5. Jab sirf view karna ho:
        function viewDiagnosisOnly() {
          populateDiagnosis(extracted);
          activateView('diagnosis-view');
        }
      
        // 6. View switch karne ke liye function
        function activateView(viewId) {
          const views = ['upload-view','about-view', 'analysis-view', 'history-view', 'contact-view'];
          views.forEach(id => {
            const section = document.getElementById(id);
            if (section) {
              section.style.display = 'none'; // sab views ko hide karo
            }
          });
      
          const activeSection = document.getElementById(viewId);
          if (activeSection) {
            activeSection.style.display = 'block'; // jo view chahiye usko show karo
          }
        }
   

        // about us js start 


        function showModal(name, role) {
          document.getElementById('modal-name').textContent = name;
          document.getElementById('modal-role').textContent = role;
          document.getElementById('modal').style.display = 'flex';
        }
  
     
  
        // Close modal when clicking outside
        window.onclick = function (event) {
          const modal = document.getElementById('modal');
          if (event.target === modal) {
            modal.style.display = 'none';
          }
        }
 



        // historry page js start 


          // Sample data for different patients
          const patientsData = {
            patient1: {
                name: "John Doe",
                id: "PT-10045",
                dob: "12/15/1982",
                gender: "Male",
                avatar: "JD",
                tests: [
                    {
                        date: "05/01/2025",
                        type: "Blood Test",
                        typeValue: "blood",
                        orderedBy: "Dr. Sarah Johnson",
                        status: "normal",
                        statusText: "Normal"
                    },
                    {
                        date: "04/15/2025",
                        type: "Cardiac Monitoring",
                        typeValue: "cardiac",
                        orderedBy: "Dr. Michael Chen",
                        status: "review",
                        statusText: "Needs Review"
                    },
                    {
                        date: "03/22/2025",
                        type: "Urine Analysis",
                        typeValue: "urine",
                        orderedBy: "Dr. Sarah Johnson",
                        status: "normal",
                        statusText: "Normal"
                    },
                    {
                        date: "02/10/2025",
                        type: "Blood Test",
                        typeValue: "blood",
                        orderedBy: "Dr. Sarah Johnson",
                        status: "abnormal",
                        statusText: "Abnormal"
                    },
                    {
                        date: "01/05/2025",
                        type: "MRI Scan",
                        typeValue: "imaging",
                        orderedBy: "Dr. Michael Chen",
                        status: "normal",
                        statusText: "Normal"
                    }
                ]
            },
            patient2: {
                name: "Jane Smith",
                id: "PT-10046",
                dob: "08/23/1975",
                gender: "Female",
                avatar: "JS",
                tests: [
                    {
                        date: "05/03/2025",
                        type: "Blood Test",
                        typeValue: "blood",
                        orderedBy: "Dr. Michael Chen",
                        status: "abnormal",
                        statusText: "Abnormal"
                    },
                    {
                        date: "04/20/2025",
                        type: "ECG",
                        typeValue: "cardiac",
                        orderedBy: "Dr. Sarah Johnson",
                        status: "normal",
                        statusText: "Normal"
                    },
                    {
                        date: "03/15/2025",
                        type: "X-Ray",
                        typeValue: "imaging",
                        orderedBy: "Dr. Michael Chen",
                        status: "review",
                        statusText: "Needs Review"
                    }
                ]
            },
            patient3: {
                name: "Robert Brown",
                id: "PT-10047",
                dob: "03/10/1990",
                gender: "Male",
                avatar: "RB",
                tests: [
                    {
                        date: "05/04/2025",
                        type: "Urine Analysis",
                        typeValue: "urine",
                        orderedBy: "Dr. Sarah Johnson",
                        status: "normal",
                        statusText: "Normal"
                    },
                    {
                        date: "04/22/2025",
                        type: "Blood Test",
                        typeValue: "blood",
                        orderedBy: "Dr. Sarah Johnson",
                        status: "normal",
                        statusText: "Normal"
                    }
                ]
            },
            patient4: {
                name: "Emma Wilson",
                id: "PT-10048",
                dob: "11/05/1965",
                gender: "Female",
                avatar: "EW",
                tests: [
                    {
                        date: "05/02/2025",
                        type: "Blood Test",
                        typeValue: "blood",
                        orderedBy: "Dr. Michael Chen",
                        status: "abnormal",
                        statusText: "Abnormal"
                    },
                    {
                        date: "04/18/2025",
                        type: "ECG",
                        typeValue: "cardiac",
                        orderedBy: "Dr. Sarah Johnson",
                        status: "review",
                        statusText: "Needs Review"
                    },
                    {
                        date: "03/10/2025",
                        type: "CT Scan",
                        typeValue: "imaging",
                        orderedBy: "Dr. Michael Chen",
                        status: "normal",
                        statusText: "Normal"
                    },
                    {
                        date: "02/15/2025",
                        type: "Urine Analysis",
                        typeValue: "urine",
                        orderedBy: "Dr. Sarah Johnson",
                        status: "normal",
                        statusText: "Normal"
                    }
                ]
            }
        };
        
        // Sample data for different users
        const usersData = {
            user1: {
                name: "Dr. BK Gupta",
                role: "Physician",
                avatar: "SJ"
            },
            user2: {
                name: "Dr. Chirag mahlotra",
                role: "Cardiologist",
                avatar: "MC"
            },
            user3: {
                name: "Alka rai",
                role: "Registered Nurse",
                avatar: "ED"
            }
        };
        
        // Set current user (would be set dynamically in a real application)
        let currentUser = usersData.user1;
        
        // Initialize the page
        document.addEventListener("DOMContentLoaded", function() {
            // Set current user info
            updateCurrentUser();
            
            // Set up event listeners
            document.getElementById("patient-select").addEventListener("change", handlePatientChange);
            document.getElementById("test-type-filter").addEventListener("change", filterResults);
            document.getElementById("date-filter").addEventListener("change", filterResults);
            document.getElementById("status-filter").addEventListener("change", filterResults);
            
            // For demonstration purposes, set a timeout to switch users
            setTimeout(() => {
                currentUser = usersData.user2;
                updateCurrentUser();
            }, 5000);
            
            setTimeout(() => {
                currentUser = usersData.user3;
                updateCurrentUser();
            }, 10000);
        });
        
        function updateCurrentUser() {
            document.getElementById("current-user-name").textContent = currentUser.name;
            document.getElementById("current-user-role").textContent = currentUser.role;
            document.getElementById("current-user-avatar").textContent = currentUser.avatar;
        }
        
        function handlePatientChange(e) {
            const patientId = e.target.value;
            
            if (!patientId) {
                clearPatientInfo();
                return;
            }
            
            // Show loading state
            document.getElementById("loading").classList.add("active");
            document.getElementById("no-data").style.display = "none";
            document.getElementById("history-table").style.display = "none";
            document.getElementById("pagination").style.display = "none";
            
            // Simulate API call delay
            setTimeout(() => {
                updatePatientInfo(patientId);
                filterResults();
                document.getElementById("loading").classList.remove("active");
            }, 1000);
        }
        
        function updatePatientInfo(patientId) {
            const patient = patientsData[patientId];
            
            if (!patient) {
                clearPatientInfo();
                return;
            }
            
            document.getElementById("patient-name").textContent = patient.name;
            document.getElementById("patient-avatar").textContent = patient.avatar;
            
            const metaHTML = `
                <div class="meta-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    DOB: ${patient.dob}
                </div>
                <div class="meta-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    ${patient.gender}
                </div>
                <div class="meta-item">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                        <polyline points="22,6 12,13 2,6"></polyline>
                    </svg>
                    ID: ${patient.id}
                </div>
            `;
            
            document.getElementById("patient-meta").innerHTML = metaHTML;
        }
        
        function clearPatientInfo() {
            document.getElementById("patient-name").textContent = "Select a patient";
            document.getElementById("patient-avatar").textContent = "";
            document.getElementById("patient-meta").innerHTML = "";
            document.getElementById("history-table").style.display = "none";
            document.getElementById("pagination").style.display = "none";
            document.getElementById("no-data").style.display = "block";
            document.getElementById("results-count").textContent = "Showing 0 results";
        }
        
        function filterResults() {
            const patientId = document.getElementById("patient-select").value;
            if (!patientId) {
                return;
            }
            
            const patient = patientsData[patientId];
            const testTypeFilter = document.getElementById("test-type-filter").value;
            const dateFilter = document.getElementById("date-filter").value;
            const statusFilter = document.getElementById("status-filter").value;
            
            // Apply filters
            let filteredTests = [...patient.tests];
            
            if (testTypeFilter) {
                filteredTests = filteredTests.filter(test => test.typeValue === testTypeFilter);
            }
            
            if (statusFilter) {
                filteredTests = filteredTests.filter(test => test.status === statusFilter);
            }
            
            if (dateFilter) {
                const today = new Date();
                let cutoffDate = new Date();
                
                switch(dateFilter) {
                    case 'week':
                        cutoffDate.setDate(today.getDate() - 7);
                        break;
                    case 'month':
                        cutoffDate.setMonth(today.getMonth() - 1);
                        break;
                    case 'quarter':
                        cutoffDate.setMonth(today.getMonth() - 3);
                        break;
                    case 'year':
                        cutoffDate.setFullYear(today.getFullYear() - 1);
                        break;
                }
                
                filteredTests = filteredTests.filter(test => {
                    const testDate = new Date(test.date);
                    return testDate >= cutoffDate;
                });
            }
            
            // Update the table
            updateTable(filteredTests);
        }
        
        function updateTable(tests) {
            const tableBody = document.getElementById("history-table-body");
            const resultsCount = document.getElementById("results-count");
            
            if (tests.length === 0) {
                document.getElementById("history-table").style.display = "none";
                document.getElementById("pagination").style.display = "none";
                document.getElementById("no-data").style.display = "block";
                document.getElementById("no-data").innerHTML = "<p>No results found for the selected filters</p>";
                resultsCount.textContent = "Showing 0 results";
                return;
            }
            
            // Update results count
            resultsCount.textContent = `Showing ${tests.length} result${tests.length === 1 ? "" : "s"}`;
            
            // Generate table rows
            let tableHTML = "";
            tests.forEach(test => {
                tableHTML += `
                    <tr>
                        <td>${test.date}</td>
                        <td>${test.type}</td>
                        <td>${test.orderedBy}</td>
                        <td>
                            <span class="status-badge status-${test.status}">${test.statusText}</span>
                        </td>
                        <td>
                            <button class="action-btn">View</button>
                            <button class="action-btn">Print</button>
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHTML;
            document.getElementById("history-table").style.display = "table";
            document.getElementById("pagination").style.display = tests.length > 10 ? "flex" : "none";
            document.getElementById("no-data").style.display = "none";
            
            // Add event listeners to buttons
            const actionButtons = document.querySelectorAll(".action-btn");
            actionButtons.forEach(button => {
                button.addEventListener("click", function() {
                    alert("Action clicked: " + this.textContent + " for test");
                });
            });
        }




        
  function activateView(viewId) {
    const views = document.querySelectorAll('section[id$="-view"]');
    views.forEach(view => view.style.display = 'none');
    document.getElementById(viewId).style.display = 'block';
  }

  // Optional: Activate only the default view on page load
  window.onload = () => activateView('upload-view');


        // khuch toh nya 


      // Main JavaScript for MEDCO Analyzer

// Global variables
let currentView = 'upload-view';
let uploadedFile = null;
let analysisCompleted = false;
let patientData = {
    patient1: {
        name: "Ansh Yadav",
        age: 28,
        gender: "Male",
        id: "MED-10056982",
        dob: "15 Mar 1997",
        history: [
            { date: "2025-05-15", type: "blood", orderedBy: "Dr. Sharma", status: "normal" },
            { date: "2025-03-10", type: "cardiac", orderedBy: "Dr. Agarwal", status: "review" },
            { date: "2025-01-22", type: "urine", orderedBy: "Dr. Mehra", status: "normal" },
            { date: "2024-11-05", type: "blood", orderedBy: "Dr. Sharma", status: "abnormal" }
        ]
    },
    patient2: {
        name: "Riti Rai",
        age: 32,
        gender: "Female",
        id: "MED-10023456",
        dob: "23 Jun 1993",
        history: [
            { date: "2025-04-27", type: "blood", orderedBy: "Dr. Patel", status: "normal" },
            { date: "2025-02-15", type: "imaging", orderedBy: "Dr. Singh", status: "normal" },
            { date: "2024-12-03", type: "urine", orderedBy: "Dr. Patel", status: "abnormal" }
        ]
    },
    patient3: {
        name: "Ayush Ranjan",
        age: 35,
        gender: "Male",
        id: "MED-10078932",
        dob: "05 Dec 1990",
        history: [
            { date: "2025-05-10", type: "cardiac", orderedBy: "Dr. Kumar", status: "review" },
            { date: "2025-04-03", type: "blood", orderedBy: "Dr. Reddy", status: "normal" },
            { date: "2025-01-15", type: "imaging", orderedBy: "Dr. Joshi", status: "normal" }
        ]
    },
    patient4: {
        name: "Ansh",
        age: 27,
        gender: "Male",
        id: "MED-10056722",
        dob: "30 Aug 1998",
        history: [
            { date: "2025-05-02", type: "blood", orderedBy: "Dr. Sharma", status: "normal" },
            { date: "2025-02-28", type: "urine", orderedBy: "Dr. Gupta", status: "normal" },
            { date: "2024-10-12", type: "cardiac", orderedBy: "Dr. Kapoor", status: "abnormal" }
        ]
    }
};

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupViewNavigation();
    setupFileUpload();
    setupPatientSelect();
    setupFilterListeners();
    setupContactForm();
    setupReportButtons();
    setupDirectNavigation(); // Add direct navigation handlers
    
    // Activate the default view
    activateView('upload-view');
    
    // Debug: Log all views
    console.log("Available views:", document.querySelectorAll('section[id$="-view"]'));
}

// Set up direct navigation handlers for key links
function setupDirectNavigation() {
    // Direct handler for About Us link - Fixed selector
    document.querySelectorAll('a[href="#about"], .about-link, a:contains("About")').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("About link clicked");
            activateView('about-view');
        });
    });
    
    // Direct handlers for other common navigation items
    const navigationMap = {
        'a[href="#upload"], .upload-link': 'upload-view',
        'a[href="#analysis"], .analysis-link': 'analysis-view',
        'a[href="#history"], .history-link': 'history-view',
        'a[href="#contact"], .contact-link': 'contact-view'
    };
    
    // Add direct handlers for each mapped item
    for (const selector in navigationMap) {
        const links = document.querySelectorAll(selector);
        const targetView = navigationMap[selector];
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                activateView(targetView);
            });
        });
    }
}

// View Navigation - Improved selector handling
function setupViewNavigation() {
    const navLinks = document.querySelectorAll('.nav-links a, nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Check for text content for specific links
            const linkText = this.textContent.trim().toLowerCase();
            if (linkText === 'about us' || linkText === 'about') {
                console.log("About Us link clicked via text content");
                activateView('about-view');
                return;
            }
            
            // Check for data-view attribute
            let viewId = this.getAttribute('data-view');
            
            // If no data-view, try to extract from href
            if (!viewId && this.getAttribute('href')) {
                const href = this.getAttribute('href');
                if (href.startsWith('#')) {
                    const potentialViewId = href.substring(1) + '-view';
                    // Check if this view exists
                    if (document.getElementById(potentialViewId)) {
                        viewId = potentialViewId;
                    }
                }
            }
            
            // If we have a view ID, activate it
            if (viewId) {
                activateView(viewId);
            }
        });
    });
}

// Function to activate a specific view
function activateView(viewId) {
    console.log("Activating view:", viewId); // Debug logging
    
    // Hide all views
    const views = document.querySelectorAll('section[id$="-view"]');
    views.forEach(view => {
        view.style.display = 'none';
        view.classList.remove('active');
    });
    
    // Show selected view
    const selectedView = document.getElementById(viewId);
    if (selectedView) {
        selectedView.style.display = 'block';
        selectedView.classList.add('active');
        currentView = viewId;
        
        console.log("View activated:", viewId); // Debug logging
        
        // Special handling for history view
        if (viewId === 'history-view') {
            initializeHistoryView();
        }
    } else {
        console.error("View not found:", viewId); // Debug logging
    }
}

// Setup report-related buttons - Fixed implementation
function setupReportButtons() {
    // View Full Report button
    const viewFullReportBtn = document.getElementById('view-full-report-btn');
    if (viewFullReportBtn) {
        viewFullReportBtn.addEventListener('click', function() {
            activateView('full-report-view');
        });
    }
    
    // Share with Doctor button
    const shareWithDoctorBtn = document.getElementById('share-with-doctor-btn');
    if (shareWithDoctorBtn) {
        shareWithDoctorBtn.addEventListener('click', function() {
            activateView('share-view');
        });
    } else {
        console.warn("Share with Doctor button not found");
    }
    
    // Export Files button
    const exportFilesBtn = document.getElementById('export-files-btn');
    if (exportFilesBtn) {
        exportFilesBtn.addEventListener('click', function() {
            activateView('export-view');
        });
    } else {
        console.warn("Export Files button not found");
    }
    
    // Back buttons for all report-related views
    const backButtons = document.querySelectorAll('.back-to-analysis');
    if (backButtons.length > 0) {
        backButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                activateView('analysis-view');
            });
        });
    } else {
        console.warn("Back buttons not found");
    }
}

// File Upload Functionality
function setupFileUpload() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const uploadBtn = document.getElementById('upload-btn');
    const progressTracker = document.getElementById('progress-tracker');
    
    if (!dropzone || !fileInput || !uploadBtn || !progressTracker) return;
    
    // Click the hidden file input when the upload button is clicked
    uploadBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    // Handle file selection
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFileUpload(this.files[0]);
        }
    });
    
    // Handle drag and drop
    dropzone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', function() {
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
}

// Function to handle the file upload process
function handleFileUpload(file) {
    uploadedFile = file;
    const dropzone = document.getElementById('dropzone');
    const progressTracker = document.getElementById('progress-tracker');
    const progressStatus = document.getElementById('progress-status');
    const steps = document.querySelectorAll('.progress-steps .step');
    
    if (!dropzone || !progressTracker || !progressStatus || steps.length === 0) {
        console.error("Missing elements for upload progress tracking");
        return;
    }
    
    // Show the progress tracker
    dropzone.style.display = 'none';
    progressTracker.classList.remove('hidden');
    
    // Simulate the upload process
    progressStatus.textContent = 'Uploading your report...';
    
    // Step 1: Upload (already active)
    setTimeout(() => {
        // Step 2: Processing
        steps[1].classList.add('actived');
        progressStatus.textContent = 'Processing your report...';
        
        setTimeout(() => {
            // Step 3: Analysis
            steps[2].classList.add('actived');
            progressStatus.textContent = 'Analyzing medical data...';
            
            setTimeout(() => {
                // Step 4: Results
                steps[3].classList.add('actived');
                progressStatus.textContent = 'Analysis complete! Viewing results...';
                
                // Mark analysis as completed
                analysisCompleted = true;
                
                // Navigate to the analysis view after a short delay
                setTimeout(() => {
                    activateView('analysis-view');
                    
                    // Make sure report action buttons are visible
                    const reportActionButtons = document.querySelector('.report-action-buttons');
                    if (reportActionButtons) {
                        reportActionButtons.style.display = 'flex';
                    }
                    
                    // Show the print/download buttons
                    const printDownloadButtons = document.querySelector('.print-download-buttons');
                    if (printDownloadButtons) {
                        printDownloadButtons.style.display = 'flex';
                    }
                }, 1000);
            }, 2000);
        }, 2000);
    }, 2000);
}

// History View Functionality
function setupPatientSelect() {
    const patientSelect = document.getElementById('patient-select');
    
    if (!patientSelect) return;
    
    patientSelect.addEventListener('change', function() {
        const selectedPatient = this.value;
        updatePatientInfo(selectedPatient);
        loadTestHistory(selectedPatient);
    });
}

function initializeHistoryView() {
    const patientSelect = document.getElementById('patient-select');
    
    if (patientSelect && patientSelect.value) {
        updatePatientInfo(patientSelect.value);
        loadTestHistory(patientSelect.value);
    } else if (patientSelect) {
        // Set default to first patient
        patientSelect.value = 'patient1';
        updatePatientInfo('patient1');
        loadTestHistory('patient1');
    } else {
        const noData = document.getElementById('no-data');
        const loading = document.getElementById('loading');
        const historyTable = document.getElementById('history-table');
        const pagination = document.getElementById('pagination');
        const resultsCount = document.getElementById('results-count');
        
        if (noData) noData.style.display = 'block';
        if (loading) loading.style.display = 'none';
        if (historyTable) historyTable.style.display = 'none';
        if (pagination) pagination.style.display = 'none';
        if (resultsCount) resultsCount.textContent = 'Showing 0 results';
    }
}

function updatePatientInfo(patientId) {
    if (!patientId || !patientData[patientId]) return;
    
    const patient = patientData[patientId];
    const patientInfo = document.getElementById('patient-info');
    const patientAvatar = document.getElementById('patient-avatar');
    const patientName = document.getElementById('patient-name');
    const patientMeta = document.getElementById('patient-meta');
    
    if (!patientInfo || !patientAvatar || !patientName || !patientMeta) return;
    
    // Update the patient avatar with initials
    const initials = patient.name.split(' ').map(n => n[0]).join('');
    patientAvatar.textContent = initials;
    
    // Update patient name
    patientName.textContent = patient.name;
    
    // Update patient metadata
    patientMeta.innerHTML = `
        <span class="meta-item">ID: ${patient.id}</span>
        <span class="meta-item">Age: ${patient.age}</span>
        <span class="meta-item">Gender: ${patient.gender}</span>
    `;
}

function loadTestHistory(patientId) {
    if (!patientId || !patientData[patientId]) return;
    
    const patient = patientData[patientId];
    const noData = document.getElementById('no-data');
    const loading = document.getElementById('loading');
    const historyTable = document.getElementById('history-table');
    const historyTableBody = document.getElementById('history-table-body');
    const pagination = document.getElementById('pagination');
    const resultsCount = document.getElementById('results-count');
    
    if (!noData || !loading || !historyTable || !historyTableBody || !pagination || !resultsCount) return;
    
    // Show loading state
    noData.style.display = 'none';
    loading.style.display = 'block';
    historyTable.style.display = 'none';
    pagination.style.display = 'none';
    
    // Simulate loading
    setTimeout(() => {
        // Hide loading
        loading.style.display = 'none';
        
        if (patient.history && patient.history.length > 0) {
            // Update the table with patient history
            historyTableBody.innerHTML = '';
            
            patient.history.forEach(test => {
                const row = document.createElement('tr');
                
                // Format date
                const testDate = new Date(test.date);
                const formattedDate = testDate.toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric' 
                });
                
                // Create a status badge class based on the status
                let statusClass = '';
                switch(test.status) {
                    case 'normal':
                        statusClass = 'status-normal';
                        break;
                    case 'abnormal':
                        statusClass = 'status-abnormal';
                        break;
                    case 'review':
                        statusClass = 'status-review';
                        break;
                }
                
                row.innerHTML = `
                    <td>${formattedDate}</td>
                    <td>${capitalizeFirstLetter(test.type)} Test</td>
                    <td>${test.orderedBy}</td>
                    <td><span class="status-badge ${statusClass}">${capitalizeFirstLetter(test.status)}</span></td>
                    <td>
                        <button class="view-btn" onclick="viewTest('${patientId}', '${test.date}')">View</button>
                        <button class="download-btn" onclick="downloadTest('${patientId}', '${test.date}')">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                        </button>
                    </td>
                `;
                
                historyTableBody.appendChild(row);
            });
            
            // Show the table and pagination
            historyTable.style.display = 'table';
            pagination.style.display = 'flex';
            resultsCount.textContent = `Showing ${patient.history.length} results`;
        } else {
            // Show no data
            noData.style.display = 'block';
            noData.innerHTML = '<p>No test history available for this patient</p>';
            resultsCount.textContent = 'Showing 0 results';
        }
    }, 1000);
}

function setupFilterListeners() {
    const filters = ['test-type-filter', 'date-filter', 'status-filter'];
    
    filters.forEach(filterId => {
        const filter = document.getElementById(filterId);
        if (filter) {
            filter.addEventListener('change', function() {
                const patientSelect = document.getElementById('patient-select');
                if (patientSelect && patientSelect.value) {
                    loadTestHistory(patientSelect.value);
                }
            });
        }
    });
}

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

// Diagnosis View Functions
function viewDiagnosisOnly() {
    activateView('diagnosis-view');
}

function showDiagnosisAndPrint() {
    viewDiagnosisOnly();
    setTimeout(() => {
        window.print();
    }, 500);
}

function downloadAsPDF() {
    // In a real implementation, this would generate and download a PDF
    alert('PDF download functionality would be implemented here');
}

// Share with Doctor functionality - Fixed implementation
function shareWithDoctor() {
    const doctorEmail = document.getElementById('doctor-email').value;
    
    if (!doctorEmail) {
        alert('Please enter a doctor email address');
        return;
    }
    
    // Simulate sending
    alert(`Report shared successfully with ${doctorEmail}`);
    
    // Return to analysis view
    activateView('analysis-view');
}

// Export files functionality - Fixed implementation
function exportFiles(format) {
    // Simulate export
    alert(`Report exported as ${format}`);
    
    // Return to analysis view
    activateView('analysis-view');
}

// Team member modal functions
function showModal(name, role) {
    const modal = document.getElementById('modal');
    const modalName = document.getElementById('modal-name');
    const modalRole = document.getElementById('modal-role');
    
    if (!modal || !modalName || !modalRole) return;
    
    modalName.textContent = name;
    modalRole.textContent = role;
    modal.style.display = 'flex';
}

function hideModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Helper Functions
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Functions for viewing and downloading test results
function viewTest(patientId, testDate) {
    if (!patientId || !testDate) return;
    
    // In a real app, this would load the specific test data
    activateView('analysis-view');
}

function downloadTest(patientId, testDate) {
    if (!patientId || !testDate) return;
    
    // In a real app, this would download the test data
    alert(`Downloading test from ${testDate} for patient ${patientData[patientId].name}`);
}


// // Custom selector for older browsers
// if (!document.querySelector('a:contains("About")')) {
//     // Polyfill for :contains selector
//     document.querySelectorAll = function(selector) {
//         if (selector.indexOf(':contains') > -1) {
//             const elements = Array.from(document.querySelectorAll('a'));
//             const searchText = selector.match(/:contains\(["'](.+)["']\)/i)[1].toLowerCase();
//             return elements.filter(el => 
//                 el.textContent.toLowerCase().includes(searchText)
//             );
//         } else {
//             return document.querySelectorAll(selector);
//         }
//     };
//  }

// Add CSS to make the views work
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS to handle view switching
    const style = document.createElement('style');
    style.textContent = `
        section:not(.active) {
            display: none;
        }
        
        #upload-view, #about-view, #analysis-view, #history-view, #contact-view, 
        #full-report-view, #diagnosis-view, #share-view, #export-view {
            display: none;
        }
        
        /* Show the about view when needed */
        #about-view.active {
            display: block !important;
        }
        
        .status-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .status-normal {
            background-color: #e6f4ea;
            color: #137333;
        }
        
        .status-abnormal {
            background-color: #fce8e6;
            color: #c5221f;
        }
        
        .status-review {
            background-color: #fef7e0;
            color: #b06000;
        }
        
        .view-btn, .download-btn {
            background: none;
            border: none;
            cursor: pointer;
            color: #1a73e8;
            margin-right: 8px;
        }
        
        .view-btn:hover, .download-btn:hover {
            text-decoration: underline;
        }
        
        .dragover {
            border-color: #1a73e8;
            background-color: rgba(26, 115, 232, 0.05);
        }
        
        .hidden {
            display: none;
        }
        
        /* Added styles for report action buttons */
        .report-action-buttons {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        
        .report-action-buttons button {
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        /* Styles for share and export views */
        .share-container, .export-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .back-to-analysis {
            background: none;
            border: none;
            color: #1a73e8;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            margin-bottom: 20px;
        }
        
        .back-to-analysis:hover {
            text-decoration: underline;
        }
    `;
    document.head.appendChild(style);
});

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
    // Fetch profile data
        fetch('/get-profile')
            .then(response => response.json())
            .then(data => {
                document.getElementById('user-name').textContent = data.name;
                document.getElementById('user-email').textContent = data.email;
                document.getElementById('user-age').textContent = data.age;
                document.getElementById('user-gender').textContent = data.gender;
            })
            .catch(error => {
                console.error('Error fetching profile:', error);
                alert('Failed to load profile data.');
            });

        // Logout function
        function logout() {
            fetch('/logout', { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        window.location.href = 'signin.html';
                    } else {
                        alert('Logout failed. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error during logout:', error);
                    alert('Logout failed. Please try again.');
                });
        }
        





  // Profile Dropdown Functionality
        function toggleProfileDropdown() {
            const dropdown = document.getElementById('profileDropdown');
            if (dropdown) {
                dropdown.classList.toggle('active');
            }
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const dropdown = document.getElementById('profileDropdown');
            const avatar = document.querySelector('.avatar');
            const profileContainer = document.querySelector('.profile-container');
            
            // Check if the click is outside the profile container
            if (!profileContainer.contains(event.target)) {
                if (dropdown && dropdown.classList.contains('active')) {
                    dropdown.classList.remove('active');
                }
            }
        });

        // Prevent dropdown from closing when clicking inside it
        document.getElementById('profileDropdown').addEventListener('click', function(event) {
            event.stopPropagation();
        });

        // Edit Profile Function
        function editProfile() {
            const profileView = document.getElementById('profile-view');
            const dropdown = document.getElementById('profileDropdown');
            
            // Close dropdown first
            if (dropdown) {
                dropdown.classList.remove('active');
            }
            
            // Show profile modal
            if (profileView) {
                profileView.classList.add('active');
            }
        }

        // Close Profile Modal
        function closeProfile() {
            const profileView = document.getElementById('profile-view');
            if (profileView) {
                profileView.classList.remove('active');
            }
        }

        // Close profile modal when clicking outside
        document.getElementById('profile-view').addEventListener('click', function(event) {
            if (event.target === this) {
                closeProfile();
            }
        });

        // Logout Function
        function logout() {
            if (confirm('Are you sure you want to logout?')) {
                // Close any open modals/dropdowns
                const dropdown = document.getElementById('profileDropdown');
                const profileView = document.getElementById('profile-view');
                
                if (dropdown) dropdown.classList.remove('active');
                if (profileView) profileView.classList.remove('active');
                
                // Simulate logout
                alert('Logged out successfully!');
                // In real implementation, redirect to login page
                // window.location.href = 'login.html';
            }
        }

        // Demo notification function
        function showNotification() {
            alert('This is a demo notification! The dropdown functionality is working correctly.');
        }

        // Escape key support
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const dropdown = document.getElementById('profileDropdown');
                const profileView = document.getElementById('profile-view');
                
                if (dropdown && dropdown.classList.contains('active')) {
                    dropdown.classList.remove('active');
                }
                
                if (profileView && profileView.classList.contains('active')) {
                    closeProfile();
                }
            }
        });

    function editProfile() {
    document.getElementById('profileDropdown').classList.remove('active');
    alert('Edit Profile functionality would open an edit form here.');
}



function logout() {
    document.getElementById('profileDropdown').classList.remove('active');
    
    if (confirm('Are you sure you want to logout?')) {
        alert('You have been successfully logged out!');
        // Add your logout logic here
        // window.location.href = 'login.html';
    }
}
