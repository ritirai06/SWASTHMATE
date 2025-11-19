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

  // Step 1: Trigger file input on button click (only if elements exist)
  if (uploadBtn && fileInput) {
    uploadBtn.addEventListener('click', () => fileInput.click());
  }

  // Step 2: On file selected (only if fileInput exists)
  if (fileInput) {
    fileInput.addEventListener('change', function () {
      const file = fileInput.files[0];
      if (!file) return;

      // Show progress UI (only if elements exist)
      if (progressTracker) {
        progressTracker.classList.remove('hidden');
      }
      if (progressSteps.length > 0 && progressStatus) {
        updateStep(0, 'Uploading your report...');
      }

      const formData = new FormData();
      formData.append('report', file);

      fetch('/upload', {
        method: 'POST',
        body: formData
      })
        .then((res) => {
          if (!res.ok) {
            return res.json().then(data => {
              throw new Error(data.message || `Server error: ${res.status}`);
            });
          }
          return res.json();
        })
        .then((data) => {
          console.log('📤 Upload response received:', data);
          console.log('📊 Response status:', data.status);
          console.log('🆔 Report ID:', data.report_id);
          console.log('📄 Filename:', data.filename);
          console.log('🔍 Has extracted_text:', !!data.extracted_text);
          console.log('🧠 Has analysis:', !!data.analysis);
          console.log('🔬 Has enhanced_analysis:', !!data.enhanced_analysis);
          console.log('💡 Has recommendations:', !!data.recommendations);
          console.log('📋 Analysis details:', data.analysis);
          console.log('🔬 Enhanced analysis:', data.enhanced_analysis);
          
          if (data.status !== 'success') {
            console.error('❌ Upload failed:', data.message || 'Unknown error');
            alert('Upload failed: ' + (data.message || 'Unknown error'));
            return;
          }

          // Step 2: Processing
          if (progressSteps.length > 0 && progressStatus) {
            updateStep(1, 'Processing with OCR and NLP...');

            setTimeout(() => {
              updateStep(2, 'Analyzing medical data...');

              setTimeout(() => {
                updateStep(3, 'Generating results...');
                
                // Store data in sessionStorage BEFORE navigation
                if (typeof sessionStorage !== 'undefined') {
                  console.log('Storing data in sessionStorage:', {
                    report_id: data.report_id,
                    filename: data.filename,
                    has_analysis: !!data.analysis,
                    has_enhanced: !!data.enhanced_analysis
                  });
                  
                  sessionStorage.setItem('reportData', JSON.stringify(data));
                  sessionStorage.setItem('report_id', data.report_id || '');
                  
                  // Verify storage
                  const stored = sessionStorage.getItem('reportData');
                  console.log('Data stored successfully:', !!stored);
                } else {
                  console.error('sessionStorage not available');
                }
                
                // Call displayResults if function exists (on current page)
                if (typeof displayResults === 'function') {
                  displayResults(data);
                } else if (typeof window.displayResults === 'function') {
                  window.displayResults(data);
                }
                
                // Navigate to analysis page after ensuring data is stored
                setTimeout(() => {
                  console.log('Navigating to /analysis');
                  window.location.href = '/analysis';
                }, 1500);
              }, 1000);
            }, 1000);
          }
        })
        .catch((err) => {
          console.error('Error:', err);
          alert('Upload failed: ' + (err.message || 'Something went wrong while processing the file.'));
        });
    });
  }

  function updateStep(index, statusText) {
    progressSteps.forEach((step, i) => {
      step.classList.toggle('actived', i <= index);
    });
    progressStatus.innerText = statusText;
  }

  // Make displayResults globally accessible
  window.displayResults = function(data) {
    globalThis.displayResults = window.displayResults;
    console.log('🎨 displayResults called with data:', data);
    console.log('📊 Data status:', data.status);
    console.log('🆔 Report ID:', data.report_id);
    console.log('📄 Filename:', data.filename);
    console.log('🧠 Analysis:', data.analysis);
    console.log('🔬 Enhanced analysis:', data.enhanced_analysis);
    
    // Store data in sessionStorage for later use
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.setItem('reportData', JSON.stringify(data));
      sessionStorage.setItem('report_id', data.report_id || '');
      console.log('💾 Data stored in sessionStorage');
    }
    
    if (progressStatus) {
      progressStatus.innerText = 'Done!';
    }
    
    // Show analysis view if it exists
    if (analysisView) {
      analysisView.style.display = 'block';
      analysisView.classList.add('active');
      console.log('✅ Analysis view displayed');
    }
    
    // Also try to find and activate analysis-view by ID
    const analysisViewById = document.getElementById('analysis-view');
    if (analysisViewById) {
      analysisViewById.style.display = 'block';
      analysisViewById.classList.add('active');
      console.log('✅ Analysis view by ID displayed');
    } else {
      console.warn('⚠️ analysis-view element not found');
    }

  // Extract patient information
  function extractPatientInfo(extractedText) {
    if (!extractedText) return {};
    
    const info = {
      name: '',
      age: '',
      gender: '',
      patientId: '',
      date: '',
      labName: ''
    };
    
    // Extract name (Mr/Mrs/Ms Name or Name: pattern)
    const nameMatch = extractedText.match(/(?:Mr\.?|Mrs\.?|Ms\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i) ||
                     extractedText.match(/Name[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i) ||
                     extractedText.match(/Prepared For\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)/i);
    if (nameMatch) info.name = nameMatch[1] || nameMatch[0];
    
    // Extract age and gender (M 25, F 30, Age: 25, etc.)
    const ageGenderMatch = extractedText.match(/([MF])\s*(\d{1,2})/i) ||
                          extractedText.match(/Age[:\-]?\s*(\d{1,2})/i);
    if (ageGenderMatch) {
      info.gender = ageGenderMatch[1] || '';
      info.age = ageGenderMatch[2] || ageGenderMatch[1] || '';
    }
    
    // Extract Patient ID
    const patientIdMatch = extractedText.match(/Patient ID[:\-]?\s*(\d+)/i);
    if (patientIdMatch) info.patientId = patientIdMatch[1];
    
    // Extract date
    const dateMatch = extractedText.match(/(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})/);
    if (dateMatch) info.date = dateMatch[1];
    
    // Extract lab name
    const labMatch = extractedText.match(/([A-Z][a-z]+\s+(?:labs|Labs|LABS))/i);
    if (labMatch) info.labName = labMatch[1];
    
    return info;
  }
  
  const extractedText = data.extracted_text || '';
  const patientInfo = extractPatientInfo(extractedText);
  const currentDate = new Date().toLocaleDateString('en-IN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  // Enhanced Analysis Summary
  const enhanced = data.enhanced_analysis || {};
  const riskAssessment = enhanced.risk_assessment || {};
  const priorityRecs = data.priority_recommendations || [];
  const drugInteractions = data.drug_interactions || [];
  
  console.log('📋 Enhanced analysis:', enhanced);
  console.log('⚠️ Risk assessment:', riskAssessment);
  console.log('🎯 Priority recommendations:', priorityRecs);
  console.log('💊 Drug interactions:', drugInteractions);

  // Enhanced Measurements Table with Normal Ranges Comparison
  const measurementsAnalysis = data.measurements_analysis || {};
  const analyzedMeasurements = measurementsAnalysis.analyzed_measurements || data.analysis.measurements || {};
  const measurementsEntries = Object.entries(analyzedMeasurements);
  console.log('📊 Measurements analysis:', measurementsAnalysis);
  console.log('📊 Analyzed measurements:', analyzedMeasurements);
  console.log('📊 Measurements entries:', measurementsEntries);
  
  let measurementsTable = '';
  if (measurementsEntries.length > 0) {
    let rowCounter = 0;
    const tableRows = measurementsEntries.map(([test, values]) => {
      if (!Array.isArray(values) || values.length === 0) return '';
      return values.map(v => {
        const value = (v && v.value !== undefined && v.value !== null) ? v.value : "-";
        const unit = (v && v.unit) ? v.unit : "-";
        
        // Use backend comparison if available, otherwise fallback
        const status = v.status || "Normal";
        const statusColor = v.status_color || "#10b981";
        const statusBg = v.status_bg || "#d1fae5";
        const statusIcon = v.status_icon || "✅";
        const normalRange = v.normal_range || "-";
        const change = v.change || "→ Stable";
        
        const rowBg = rowCounter % 2 === 0 ? '#ffffff' : '#f8fafc';
        rowCounter++;
        return `
          <tr style="background: ${rowBg}; border-bottom: 1px solid #e5e7eb; transition: all 0.2s ease;" 
              onmouseover="this.style.background='#f1f5f9';" 
              onmouseout="this.style.background='${rowBg}';">
            <td style="padding: 1rem; font-weight: 700; color: #1e293b;">${test}</td>
            <td style="padding: 1rem; font-weight: 700; color: #1e293b; font-size: 1.1rem;">${value}</td>
            <td style="padding: 1rem; color: #64748b;">${unit}</td>
            <td style="padding: 1rem;">
              <span style="background: ${statusBg}; color: ${statusColor}; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 0.875rem;">
                ${statusIcon} ${status}
              </span>
            </td>
            <td style="padding: 1rem; color: #64748b; font-size: 0.9rem;">${normalRange}</td>
          </tr>
        `;
      }).join('');
    }).filter(row => row).join('');
    
    const abnormalCount = measurementsAnalysis.abnormal_count || 0;
    const totalTests = measurementsAnalysis.total_tests || measurementsEntries.length;
    
    measurementsTable = `
      <div class="section-header-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.25rem 1.5rem; border-radius: 12px 12px 0 0; margin: 2rem 0 0 0; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem; justify-content: space-between;">
          <span>📈 Laboratory Test Results</span>
          <span style="font-size: 0.9rem; background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
            ${abnormalCount > 0 ? `⚠️ ${abnormalCount} Abnormal` : '✅ All Normal'} (${totalTests} Tests)
          </span>
        </h2>
      </div>
      <div class="section-content-wrapper" style="background: white; border-radius: 0 0 12px 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); margin-bottom: 2rem;">
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; background: white; margin-top: 0;">
            <thead>
              <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <th style="padding: 1rem; text-align: left; font-weight: 600; border-radius: 8px 0 0 0;">Test Name</th>
                <th style="padding: 1rem; text-align: left; font-weight: 600;">Value</th>
                <th style="padding: 1rem; text-align: left; font-weight: 600;">Unit</th>
                <th style="padding: 1rem; text-align: left; font-weight: 600;">Status</th>
                <th style="padding: 1rem; text-align: left; font-weight: 600; border-radius: 0 8px 0 0;">Normal Range</th>
              </tr>
            </thead>
            <tbody>
              ${tableRows || '<tr><td colspan="5" style="padding: 20px; text-align: center; color: #64748b;">No measurements found</td></tr>'}
            </tbody>
          </table>
        </div>
        ${abnormalCount > 0 ? `
        <div style="margin-top: 1.5rem; padding: 1rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 10px; border-left: 4px solid #d97706;">
          <p style="margin: 0; color: #92400e; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
            <span>⚠️</span>
            <span>${abnormalCount} out of ${totalTests} tests show abnormal values</span>
          </p>
        </div>
        ` : ''}
      </div>
    `;
  } else {
    measurementsTable = `
      <div style="background: #f8fafc; border-radius: 12px; padding: 24px; margin: 20px 0; text-align: center; color: #64748b;">
        <p style="margin: 0;">📊 No lab measurements detected in this report.</p>
      </div>
    `;
  }

  // Risk Score Badge
  const riskColor = riskAssessment.level === 'High' ? '#ef4444' : 
                    riskAssessment.level === 'Moderate' ? '#f59e0b' : '#10b981';
  const riskBadge = `<div style="background: ${riskColor}15; border-left: 4px solid ${riskColor}; padding: 15px; margin: 15px 0; border-radius: 5px;">
    <h3 style="margin: 0 0 10px 0; color: ${riskColor};">⚠️ Health Risk Assessment: ${riskAssessment.level || 'Low'}</h3>
    <p style="margin: 5px 0;"><strong>Risk Score:</strong> ${riskAssessment.score || 0}/100</p>
    <p style="margin: 5px 0;">${riskAssessment.recommendation || ''}</p>
    ${riskAssessment.factors && riskAssessment.factors.length > 0 ? 
      `<p style="margin: 5px 0;"><strong>Key Risk Factors:</strong> ${riskAssessment.factors.join(', ')}</p>` : ''}
  </div>`;

  // Summary - check multiple possible element IDs
  const contentElement = analysisContent || 
                         document.getElementById('analysis-result') || 
                         document.getElementById('analysis-content') ||
                         document.querySelector('#analysis-view #analysis-result') ||
                         document.querySelector('.analysis-container #analysis-result');
  
  if (!contentElement) {
    console.error('Analysis content element not found. Available IDs:', {
      'analysisContent': !!analysisContent,
      'analysis-result': !!document.getElementById('analysis-result'),
      'analysis-content': !!document.getElementById('analysis-content'),
      'analysis-view': !!document.getElementById('analysis-view')
    });
    // Try to create or find any container
    const analysisView = document.getElementById('analysis-view');
    if (analysisView) {
      const fallbackDiv = document.createElement('div');
      fallbackDiv.id = 'analysis-result';
      analysisView.appendChild(fallbackDiv);
      return window.displayResults(data); // Retry with new element
    }
    return;
  }
  
  console.log('📝 Populating contentElement with data');
  contentElement.innerHTML = `
    ${riskBadge}
    
    ${measurementsTable}
    
    <div style="background: #f0f7ff; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #3b82f6;">
      <h3 style="margin: 0 0 10px 0; color: #1d4ed8;">📊 Analysis Summary</h3>
      <p style="white-space: pre-line; margin: 0;">${enhanced.summary_text || 'Analysis complete.'}</p>
    </div>
    
    ${enhanced.key_insights && enhanced.key_insights.length > 0 ? `
    <div style="background: #fff7ed; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #f59e0b;">
      <h3 style="margin: 0 0 10px 0; color: #d97706;">💡 Key Insights</h3>
      <ul style="margin: 0; padding-left: 20px;">
        ${enhanced.key_insights.map(insight => `<li style="margin: 5px 0;">${insight}</li>`).join('')}
      </ul>
    </div>` : ''}

    <!-- Report Header -->
    <div style="background: white; padding: 2rem; border-bottom: 2px solid #e5e7eb; margin-bottom: 2rem;">
      <h1 style="font-size: 1.75rem; font-weight: 600; color: #1e293b; margin: 0 0 0.5rem 0;">Medical Report Analysis</h1>
      <p style="color: #64748b; margin: 0; font-size: 0.9rem;">Report ID: ${data.report_id || 'N/A'} | File: ${data.filename || 'N/A'}</p>
    </div>
    
    <!-- Patient Information Section -->
    <div style="background: #f8fafc; padding: 1.5rem; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 2rem;">
      <h2 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e5e7eb;">Patient Information</h2>
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
        <div style="padding: 0.75rem; background: white; border-radius: 6px; border-left: 3px solid #667eea;">
          <div style="font-size: 0.875rem; color: #64748b; font-weight: 500; margin-bottom: 0.25rem;">Patient Name:</div>
          <div style="font-size: 1rem; color: #1e293b; font-weight: 600;">${patientInfo.name || 'Not Available'}</div>
        </div>
        <div style="padding: 0.75rem; background: white; border-radius: 6px; border-left: 3px solid #667eea;">
          <div style="font-size: 0.875rem; color: #64748b; font-weight: 500; margin-bottom: 0.25rem;">Age:</div>
          <div style="font-size: 1rem; color: #1e293b; font-weight: 600;">${patientInfo.age || 'Not Available'}</div>
        </div>
        <div style="padding: 0.75rem; background: white; border-radius: 6px; border-left: 3px solid #667eea;">
          <div style="font-size: 0.875rem; color: #64748b; font-weight: 500; margin-bottom: 0.25rem;">Gender:</div>
          <div style="font-size: 1rem; color: #1e293b; font-weight: 600;">${patientInfo.gender || 'Not Available'}</div>
        </div>
        <div style="padding: 0.75rem; background: white; border-radius: 6px; border-left: 3px solid #667eea;">
          <div style="font-size: 0.875rem; color: #64748b; font-weight: 500; margin-bottom: 0.25rem;">Patient ID:</div>
          <div style="font-size: 1rem; color: #1e293b; font-weight: 600;">${patientInfo.patientId || data.report_id || 'N/A'}</div>
        </div>
        ${patientInfo.labName ? `
        <div style="padding: 0.75rem; background: white; border-radius: 6px; border-left: 3px solid #667eea;">
          <div style="font-size: 0.875rem; color: #64748b; font-weight: 500; margin-bottom: 0.25rem;">Laboratory:</div>
          <div style="font-size: 1rem; color: #1e293b; font-weight: 600;">${patientInfo.labName}</div>
        </div>
        ` : ''}
        <div style="padding: 0.75rem; background: white; border-radius: 6px; border-left: 3px solid #667eea;">
          <div style="font-size: 0.875rem; color: #64748b; font-weight: 500; margin-bottom: 0.25rem;">Test Date:</div>
          <div style="font-size: 1rem; color: #1e293b; font-weight: 600;">${patientInfo.date || currentDate}</div>
        </div>
        <div style="padding: 0.75rem; background: white; border-radius: 6px; border-left: 3px solid #667eea;">
          <div style="font-size: 0.875rem; color: #64748b; font-weight: 500; margin-bottom: 0.25rem;">Generated On:</div>
          <div style="font-size: 1rem; color: #1e293b; font-weight: 600;">${currentDate}</div>
        </div>
      </div>
    </div>
    
    ${(data.analysis.diseases || []).length > 0 ? `
    <div style="margin: 2rem 0;">
      <h2 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e5e7eb;">Detected Medical Conditions</h2>
      <ul style="list-style: none; padding: 0; margin: 0;">
        ${(data.analysis.diseases || []).map(d => `<li style="padding: 0.75rem; margin: 0.5rem 0; background: #f8fafc; border-left: 3px solid #667eea; border-radius: 4px; color: #1e293b;">${d}</li>`).join('')}
      </ul>
    </div>
    ` : ''}
    
    ${measurementsAnalysis.abnormal_tests && measurementsAnalysis.abnormal_tests.length > 0 ? `
    <div style="background: #fff7ed; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #f59e0b;">
      <h3 style="margin: 0 0 10px 0; color: #d97706;">⚠️ Abnormal Lab Values Detected</h3>
      <ul style="margin: 0; padding-left: 20px;">
        ${measurementsAnalysis.abnormal_tests.map(test => `
          <li style="margin: 5px 0;">
            <strong>${test.test}</strong>: ${test.value} ${test.unit} 
            <span style="color: ${test.status === 'High' ? '#ef4444' : '#f59e0b'}; font-weight: 600;">
              (${test.status} - Normal: ${test.normal_range})
            </span>
          </li>
        `).join('')}
      </ul>
    </div>` : ''}
    

    ${drugInteractions.length > 0 ? `
    <div style="margin: 2rem 0;">
      <h2 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e5e7eb;">Drug Interactions</h2>
      <ul style="list-style: none; padding: 0; margin: 0;">
        ${drugInteractions.map(interaction => {
          const drug1 = interaction.medication1 || interaction.drug1 || 'Unknown';
          const drug2 = interaction.medication2 || interaction.drug2 || 'Unknown';
          const description = interaction.description || interaction.interaction_type || '';
          const action = interaction.recommendation || interaction.action || 'Consult your doctor';
          return `
          <li style="padding: 0.75rem; margin: 0.5rem 0; background: #fef2f2; border-left: 3px solid #dc2626; border-radius: 4px; color: #1e293b;">
            <strong>${drug1}</strong> + <strong>${drug2}</strong>
            ${description ? `<div style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">${description}</div>` : ''}
            <div style="color: #dc2626; font-weight: 500; margin-top: 0.5rem;">→ ${action}</div>
          </li>
        `;
        }).join('')}
      </ul>
    </div>` : ''}

    ${(data.recommendations || []).length > 0 ? `
    <div style="margin: 2rem 0;">
      <h2 style="font-size: 1.25rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e5e7eb;">General Recommendations</h2>
      <ul style="list-style: none; padding: 0; margin: 0;">
        ${(data.recommendations || []).map(r => `<li style="padding: 0.75rem; margin: 0.5rem 0; background: #f8fafc; border-left: 3px solid #10b981; border-radius: 4px; color: #1e293b;">${r}</li>`).join('')}
      </ul>
    </div>
    ` : ''}
  `;

  // Diagnosis content - check if element exists
  const diagnosisElement = diagnosisContent || document.getElementById('diagnosis-content');
  if (diagnosisElement) {
    diagnosisElement.innerHTML = `
    ${riskBadge}
    ${enhanced.summary_text ? `<div style="background: #f0f7ff; padding: 15px; margin: 15px 0; border-radius: 5px;">
      <h3>📋 Executive Summary</h3>
      <p style="white-space: pre-line;">${enhanced.summary_text}</p>
    </div>` : ''}
    
    ${measurementsTable}

    ${(data.analysis.diseases || []).length > 0 ? `
    <div class="section-header-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.25rem 1.5rem; border-radius: 12px 12px 0 0; margin: 2rem 0 0 0;">
      <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">🦠 Detected Medical Conditions</h2>
    </div>
    <div class="section-content-wrapper" style="background: white; border-radius: 0 0 12px 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); margin-bottom: 2rem;">
      ${(data.analysis.diseases || []).map(d => `
        <div class="disease-card" style="background: white; border: 2px solid #e5e7eb; border-radius: 12px; padding: 1.25rem; margin: 0.75rem 0; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06); display: flex; align-items: center; gap: 1rem;">
          <span style="font-size: 1.5rem;">🦠</span>
          <span>${d}</span>
        </div>
      `).join('')}
    </div>
    ` : ''}

    <h4>💊 Medications</h4>
    ${data.analysis.medications && data.analysis.medications.length > 0 ? 
      `<ul>${data.analysis.medications.map(m => {
        const med = typeof m === 'string' ? m : (m.name || m.canonical || 'Unknown');
        return `<li>${med}</li>`;
      }).join('')}</ul>` : 
      '<p>No medications detected.</p>'}

    <h4>👨‍⚕️  Suggested Specialization</h4>
    <p style="padding: 12px; background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 4px; font-weight: 600; color: #1e40af;">
      ${data.analysis.specialization || 'General Physician'}
    </p>


    ${drugInteractions.length > 0 ? `
    <h4>⚠️ Drug Interactions</h4>
    <ul>
      ${drugInteractions.map(interaction => `
        <li style="margin: 10px 0; color: #dc2626;">
          <strong>${interaction.drug1}</strong> + <strong>${interaction.drug2}</strong>
          <br>${interaction.description}
          <br><em>${interaction.action}</em>
        </li>
      `).join('')}
    </ul>` : ''}

    ${(data.recommendations || []).length > 0 ? `
    <div class="section-header-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.25rem 1.5rem; border-radius: 12px 12px 0 0; margin: 2rem 0 0 0;">
      <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">💡 General Recommendations</h2>
    </div>
    <div class="section-content-wrapper" style="background: white; border-radius: 0 0 12px 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); margin-bottom: 2rem;">
      ${(data.recommendations || []).map(r => `
        <div class="general-rec-card" style="background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 1rem 1.25rem; margin: 0.5rem 0; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05); display: flex; align-items: flex-start; gap: 0.75rem;">
          <span style="font-size: 1.25rem; flex-shrink: 0;">💡</span>
          <span>${r}</span>
        </div>
      `).join('')}
    </div>
    ` : ''}
  `;

  // Debug
  console.log('✅ displayResults completed successfully');
  console.log('📊 Final Enhanced Analysis:', enhanced);
  console.log('🎯 Final Priority Recommendations:', priorityRecs);
  console.log('💊 Final Drug Interactions:', drugInteractions);
  };


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
    
    // Function to show notification
    function showNotification(message, type) {
        // Remove existing notifications
        const existing = document.querySelector('.contact-notification');
        if (existing) existing.remove();
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `contact-notification ${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'success') {
            notification.style.backgroundColor = '#10b981';
        } else {
            notification.style.backgroundColor = '#ef4444';
        }
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
    
    // Add CSS animation if not exists
    if (!document.getElementById('contact-notification-styles')) {
        const style = document.createElement('style');
        style.id = 'contact-notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Add event listener to the contact form
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Get form data
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const query = document.getElementById('query');
            
            if (!name || !email || !query) return;
            
            const nameValue = name.value.trim();
            const emailValue = email.value.trim();
            const queryValue = query.value.trim();
            
            // Form validation
            if (!nameValue || !emailValue || !queryValue) {
                showNotification('Please fill in all fields', 'error');
                return;
            }
            
            // Email validation
            if (!isValidEmail(emailValue)) {
                showNotification('Please enter a valid email address', 'error');
                return;
            }
            
            // Prepare data to send
            const formData = {
                name: nameValue,
                email: emailValue,
                query: queryValue,
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
                    const errorMsg = error.message || 'Failed to send your message. Please try again later.';
                    showNotification(errorMsg, 'error');
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
        const apiEndpoint = '/api/contact';
        
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || `HTTP error! Status: ${response.status}`);
        }
        
        return result;
    }
    
    // Function to validate email format
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});


  

