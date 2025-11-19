  // Profile Dropdown Functionality
        function toggleProfileDropdown() {
            const dropdown = document.getElementById('profileDropdownModern');
            if (dropdown) {
                dropdown.classList.toggle('active');
            }
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            const dropdown = document.getElementById('profileDropdownModern');
            const profileContainer = document.getElementById('profileButtonContainer');
            
            // Check if the click is outside the profile container
            if (profileContainer && !profileContainer.contains(event.target)) {
                if (dropdown && dropdown.classList.contains('active')) {
                    dropdown.classList.remove('active');
                }
            }
        });

        // Prevent dropdown from closing when clicking inside it
        const profileDropdown = document.getElementById('profileDropdownModern');
        if (profileDropdown) {
            profileDropdown.addEventListener('click', function(event) {
                event.stopPropagation();
            });
        }

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
    if (confirm('Are you sure you want to logout?')) {
        // Clear login data
        localStorage.removeItem('userData');

        // Hide profile, show login button
        document.querySelector('.profile-container').style.display = 'none';
        document.querySelector('.sign').style.display = 'block';

        // Optional: Redirect to sign-in page
        window.location.href = '/signin';
    }
}




// On Home page load, update profile UI with stored data
document.addEventListener('DOMContentLoaded', function () {
    const userData = JSON.parse(localStorage.getItem('userData'));

    if (userData && userData.loggedIn) {
        // Show profile container, hide login button (check if elements exist)
        const profileContainer = document.querySelector('.profile-container');
        const signElement = document.querySelector('.sign');
        if (profileContainer) profileContainer.style.display = 'flex';
        if (signElement) signElement.style.display = 'none';

        // Set avatar initial (check if elements exist)
        const avatarInitial = userData.name ? userData.name.charAt(0).toUpperCase() : 'U';
        const avatarM = document.querySelector('.avatar .m');
        const profileAvatar = document.querySelector('.profile-avatar');
        if (avatarM) avatarM.textContent = avatarInitial;
        if (profileAvatar) profileAvatar.textContent = avatarInitial;

        // Set dropdown profile info (check if elements exist)
        const dropdownName = document.getElementById('dropdown-user-name');
        const dropdownEmail = document.getElementById('dropdown-user-email');
        if (dropdownName) dropdownName.textContent = userData.name || 'User';
        if (dropdownEmail) dropdownEmail.textContent = userData.email || 'user@example.com';

        // Also update profile modal view (if visible)
        const userName = document.getElementById('user-name');
        const userEmail = document.getElementById('user-email');
        if (userName) userName.textContent = userData.name || 'User';
        if (userEmail) userEmail.textContent = userData.email || 'user@example.com';
    } else {
        // Not logged in: hide profile and show login button
        const profileContainer = document.querySelector('.profile-container');
        const signElement = document.querySelector('.sign');
        if (profileContainer) profileContainer.style.display = 'none';
        if (signElement) signElement.style.display = 'block';
    }
});
// Load user profile data into form when editing
function editProfile() {
  const user = JSON.parse(localStorage.getItem('userData'));
  if (!user) return;

  document.getElementById('edit-name').value = user.name || '';
  document.getElementById('edit-email').value = user.email || '';
  document.getElementById('edit-password').value = user.password || '';
  document.getElementById('profile-view').style.display = 'block';
}

// Close the modal
function closeProfile() {
  document.getElementById('profile-view').style.display = 'none';
}

// Save updated profile data
document.getElementById('edit-profile-form').addEventListener('submit', function (e) {
  e.preventDefault();

  const updatedUser = {
    name: document.getElementById('edit-name').value,
    email: document.getElementById('edit-email').value,
    password: document.getElementById('edit-password').value,
    loggedIn: true
  };

  localStorage.setItem('userData', JSON.stringify(updatedUser));
  document.getElementById('profile-view').style.display = 'none';
  updateProfileUI();
  alert('Profile updated successfully!');
});

// Refresh UI with current profile info
function updateProfileUI() {
  const user = JSON.parse(localStorage.getItem('userData'));

  if (user && user.loggedIn) {
    const profileContainer = document.querySelector('.profile-container');
    const signElement = document.querySelector('.sign');
    if (profileContainer) profileContainer.style.display = 'flex';
    if (signElement) signElement.style.display = 'none';

    const initial = user.name ? user.name.charAt(0).toUpperCase() : 'U';
    const avatarM = document.querySelector('.avatar .m');
    const profileAvatar = document.querySelector('.profile-avatar');
    if (avatarM) avatarM.textContent = initial;
    if (profileAvatar) profileAvatar.textContent = initial;

    const dropdownName = document.getElementById('dropdown-user-name');
    const dropdownEmail = document.getElementById('dropdown-user-email');
    if (dropdownName) dropdownName.textContent = user.name || 'User';
    if (dropdownEmail) dropdownEmail.textContent = user.email || 'user@example.com';
  } else {
    const profileContainer = document.querySelector('.profile-container');
    const signElement = document.querySelector('.sign');
    if (profileContainer) profileContainer.style.display = 'none';
    if (signElement) signElement.style.display = 'block';
  }
}

// On page load, update the profile view if logged in
document.addEventListener('DOMContentLoaded', function () {
  updateProfileUI();
});


document.addEventListener('DOMContentLoaded', function () {
    const skipPages = ['/upload', '/prescription-reader.html', '/about', '/about.html','/','/index.html']; // pages that DON'T require login
    const path = window.location.pathname;

    const userData = JSON.parse(localStorage.getItem('userData'));

    if (!userData || !userData.loggedIn) {
        if (!skipPages.includes(path)) {
            alert('Please log in to access this page.');
            window.location.href = '/signin';
        }
    }
});

function toggleMenu() {
    document.querySelector(".nav-links").classList.toggle("active");
  }



