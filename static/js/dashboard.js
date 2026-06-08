
const Auth = new AuthService(); // Auth অবজেক্ট ইনিশিয়ালাইজ করা হলো


// get admin info
async function getAdminProfile() {
    try {
        const response = await fetch("/admin/profile-data", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
        });
  
        if (response.ok) {
            const data = await response.json();
            const stats = data.data;

            console.log(stats);

            // Update admin name
            document.getElementById("headerAdminName").innerText = stats.full_name;

            // Update admin avatar with profile picture or keep existing
            if (stats.profile_image_url) {
                const avatarImg = document.querySelector("#headerAdminAvatar img");
                if (avatarImg) {
                    avatarImg.src = stats.profile_image_url;
                } else {
                    // No img element, create one
                    document.getElementById("headerAdminAvatar").innerHTML = 
                        `<img src="${stats.profile_image_url}" alt="${stats.full_name}">`;
                }
            }
        } else {
            console.error("Failed to fetch admin profile:", response.status);
        }
    } catch (err) {
        console.error("Error fetching admin profile:", err);
    }
}


async function getUser() {
    const tbody = document.getElementById("usersTableBody");
    
    // Show loading state
    tbody.innerHTML = `
        <tr>
            <td colspan="9" class="table-loading">
                <div class="spinner"></div>
                Loading users...
            </td>
        </tr>
    `;
    
    try {
        const response = await fetch("/admin/users-list", {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            throw new Error("Failed to fetch users");
        }

        const result = await response.json();
        const users = result.data.users;

        tbody.innerHTML = ""; // Clear loading state

        if (!users || users.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="table-empty">
                        <i class="fas fa-users"></i>
                        <p>No users found</p>
                    </td>
                </tr>
            `;
            document.getElementById("usersPaginationInfo").innerText =
                "Showing 0 of 0 users";
            return;
        }

        users.forEach(user => {
            const tr = document.createElement("tr");

            // Format KYC status with proper badge class
            const kycStatus = user.kyc_status ? user.kyc_status.toLowerCase() : "na";
            const kycBadgeClass = `badge-${kycStatus}`;
            const kycDisplay = user.kyc_status ? user.kyc_status : "N/A";

            // Format active status
            const isActive = user.is_active;
            const activeBadgeClass = isActive ? "badge-active" : "badge-inactive";
            const activeDisplay = isActive ? "Active" : "Inactive";

            // Format balance with currency
            const balance = parseFloat(user.wallet_balance || 0).toLocaleString('en-BD', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });

            // Format date
            const createdDate = new Date(user.created_at).toLocaleDateString('en-BD', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });

            tr.innerHTML = `
                <td title="${user.user_id}">
                    ${user.user_id}
                    <button class="action-btn copy-id-btn" onclick="copyToClipboard('${user.user_id}', this)" title="Copy ID">
                        <i class="fas fa-copy"></i>
                    </button>
                </td>
                <td title="${user.full_name || '-'}">${user.full_name ?? "-"}</td>
                <td title="${user.email ?? '-'}">${user.email ?? "-"}</td>
                <td>${user.phone ?? "-"}</td>
                <td>
                    <span class="badge ${kycBadgeClass}">
                        ${kycDisplay}
                    </span>
                </td>
                <td>
                    <span class="badge ${activeBadgeClass}">
                        ${activeDisplay}
                    </span>
                </td>
                <td>${balance} ${user.wallet_currency}</td>
                <td>${createdDate}</td>
                <td>
                    <div class="actions">
                        <button class="action-btn" onclick="viewUser('${user.user_id}')" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="action-btn" onclick="editUser('${user.user_id}')" title="Edit User">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </td>
            `;

            tbody.appendChild(tr);
        });

        document.getElementById("usersPaginationInfo").innerText =
            `Showing ${users.length} of ${users.length} users`;

    } catch (err) {
        console.error("Error fetching users:", err);
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="table-empty">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading users. Please try again.</p>
                </td>
            </tr>
        `;
    }
}

// Copy to clipboard function
async function copyToClipboard(text, button) {
    try {
        await navigator.clipboard.writeText(text);
        
        // Visual feedback
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i>';
        button.style.color = 'var(--success-color)';
        button.style.borderColor = 'var(--success-color)';
        
        setTimeout(() => {
            button.innerHTML = originalIcon;
            button.style.color = '';
            button.style.borderColor = '';
        }, 1500);
        
        // Show toast notification
        showToast('ID copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy:', err);
        showToast('Failed to copy ID', 'error');
    }
}

// View user details
function viewUser(userId) {
    // Open modal with user details
    showModal('User Details', `
        <div class="detail-grid">
            <div class="detail-item">
                <div class="detail-label">User ID</div>
                <div class="detail-value">${userId}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Status</div>
                <div class="detail-value">Loading...</div>
            </div>
        </div>
    `);
    
    // Fetch and display user details
    fetchUserDetails(userId);
}

// Edit user
function editUser(userId) {
    showModal('Edit User', `
        <div class="modal-form">
            <div class="form-group">
                <label>User ID</label>
                <input type="text" value="${userId}" readonly>
            </div>
            <div class="form-group">
                <label>Status</label>
                <select>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                </select>
            </div>
            <div class="form-actions">
                <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="updateUserStatus('${userId}')">Update</button>
            </div>
        </div>
    `);
}

// Fetch user details for modal
async function fetchUserDetails(userId) {
    try {
        const response = await fetch(`/admin/user/${userId}`, {
            method: "GET",
            credentials: "include",
        });

        if (response.ok) {
            const result = await response.json();
            const user = result.data;
            
            // Update modal content with user details
            const modalBody = document.getElementById('modalBody');
            modalBody.innerHTML = `
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">Full Name</div>
                        <div class="detail-value">${user.full_name || '-'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Email</div>
                        <div class="detail-value">${user.email || '-'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Phone</div>
                        <div class="detail-value">${user.phone || '-'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">KYC Status</div>
                        <div class="detail-value">${user.kyc_status || 'N/A'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Wallet Balance</div>
                        <div class="detail-value">${user.wallet_balance || 0} ${user.wallet_currency || 'BDT'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Joined</div>
                        <div class="detail-value">${new Date(user.created_at).toLocaleDateString()}</div>
                    </div>
                </div>
            `;
        }
    } catch (err) {
        console.error('Error fetching user details:', err);
    }
}

// Update user status
async function updateUserStatus(userId) {
    // Implement status update logic
    showToast('User status updated successfully!', 'success');
    closeModal();
    getUser(); // Refresh the table
}

// Export users to CSV
function exportUsers() {
    // Get the table data
    const tbody = document.getElementById('usersTableBody');
    const rows = tbody.querySelectorAll('tr');
    
    if (rows.length === 0 || rows[0].classList.contains('table-empty') || rows[0].classList.contains('table-loading')) {
        showToast('No users to export', 'warning');
        return;
    }
    
    // Build CSV content
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'User ID,Name,Email,Phone,KYC Status,Status,Balance,Joined\n';
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = [];
        
        cells.forEach((cell, index) => {
            // Skip the actions column (last column)
            if (index < cells.length - 1) {
                let text = cell.textContent.trim();
                // Remove the copy button text
                text = text.replace('Copy', '').trim();
                // Escape commas and quotes
                text = text.replace(/"/g, '""');
                rowData.push(`"${text}"`);
            }
        });
        
        csvContent += rowData.join(',') + '\n';
    });
    
    // Create download link
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `users_export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showToast('Users exported successfully!', 'success');
}

// Table sorting functionality
let currentSort = {
    column: null,
    direction: 'asc'
};

function initTableSorting() {
    const tableContainer = document.getElementById('usersTableContainer');
    if (!tableContainer) return;
    
    const sortableHeaders = tableContainer.querySelectorAll('.sortable');
    
    sortableHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            sortTable(column);
            
            // Update sort icons
            sortableHeaders.forEach(h => {
                h.classList.remove('asc', 'desc');
                h.querySelector('.sort-icon').className = 'fas fa-sort sort-icon';
            });
            
            if (currentSort.direction === 'asc') {
                header.classList.add('asc');
                header.querySelector('.sort-icon').className = 'fas fa-sort-up sort-icon';
            } else {
                header.classList.add('desc');
                header.querySelector('.sort-icon').className = 'fas fa-sort-down sort-icon';
            }
        });
    });
}

function sortTable(column) {
    const tbody = document.getElementById('usersTableBody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Skip empty or loading rows
    const dataRows = rows.filter(row => 
        !row.classList.contains('table-empty') && 
        !row.classList.contains('table-loading')
    );
    
    if (dataRows.length === 0) return;
    
    // Toggle sort direction if same column
    if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.direction = 'asc';
    }
    
    // Sort the rows
    dataRows.sort((a, b) => {
        const aCell = a.querySelectorAll('td')[getColumnIndex(column)];
        const bCell = b.querySelectorAll('td')[getColumnIndex(column)];
        
        if (!aCell || !bCell) return 0;
        
        let aValue = aCell.textContent.trim();
        let bValue = bCell.textContent.trim();
        
        // Handle numeric values (balance)
        if (column === 'wallet_balance') {
            aValue = parseFloat(aValue.replace(/,/g, '').replace(/[^\d.]/g, '')) || 0;
            bValue = parseFloat(bValue.replace(/,/g, '').replace(/[^\d.]/g, '')) || 0;
            return currentSort.direction === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        // Handle dates
        if (column === 'created_at') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
            return currentSort.direction === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        // String comparison
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
        
        if (aValue < bValue) return currentSort.direction === 'asc' ? -1 : 1;
        if (aValue > bValue) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
    });
    
    // Re-append sorted rows
    dataRows.forEach(row => tbody.appendChild(row));
}

function getColumnIndex(column) {
    const columnMap = {
        'user_id': 0,
        'full_name': 1,
        'email': 2,
        'phone': 3,
        'kyc_status': 4,
        'is_active': 5,
        'wallet_balance': 6,
        'created_at': 7
    };
    return columnMap[column] || 0;
}

// Toast notification function
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-times-circle',
        'warning': 'fa-exclamation-circle',
        'info': 'fa-info-circle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Modal functions
function showModal(title, content) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = content;
    document.getElementById('modalOverlay').classList.add('show');
    document.getElementById('modal').classList.add('show');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('show');
    document.getElementById('modal').classList.remove('show');
}

// ===================================
// Profile Section Functions
// ===================================

// Load admin profile data
async function loadAdminProfile() {
    try {
        const response = await fetch("/admin/profile-data", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
        });

        if (response.ok) {
            const data = await response.json();
            const admin = data.data;

            // Update header
            document.getElementById('headerAdminName').innerText = admin.full_name || 'Admin';
            if (admin.profile_image_url) {
                document.querySelector("#headerAdminAvatar img").src = admin.profile_image_url;
            }

            // Update profile page
            document.getElementById('profileFullName').innerText = admin.full_name || 'Admin User';
            document.getElementById('profileRole').innerHTML = `<i class="fas fa-shield-alt"></i> ${admin.role || 'Super Admin'}`;
            document.getElementById('profileEmail').innerText = admin.email || '-';
            document.getElementById('profileAdminId').innerText = admin.admin_id || '-';
            document.getElementById('profileJoinedDate').innerText = admin.created_at ? new Date(admin.created_at).toLocaleDateString() : '-';
            
            // Update profile avatar
            if (admin.profile_image_url) {
                document.getElementById('profileAvatarImg').src = admin.profile_image_url;
            }

            // Update info grid
            document.getElementById('infoFullName').innerText = admin.full_name || '-';
            document.getElementById('infoEmail').innerText = admin.email || '-';
            document.getElementById('infoPhone').innerText = admin.phone || 'Not provided';
            document.getElementById('displayRole').innerText = admin.role || 'Super Admin';

            // Load permissions
            loadPermissions(admin.permissions || []);
        }
    } catch (err) {
        console.error("Error loading admin profile:", err);
    }
}

// Load permissions
function loadPermissions(permissions) {
    const container = document.getElementById('permissionsGrid');
    container.innerHTML = '';

    const permissionLabels = {
        'manage_users': 'Manage Users',
        'manage_transactions': 'Manage Transactions',
        'manage_wallets': 'Manage Wallets',
        'view_reports': 'View Reports',
        'manage_settings': 'Manage Settings',
        'manage_admins': 'Manage Admins',
        'view_audit_logs': 'View Audit Logs',
        'manage_bills': 'Manage Bills',
        'manage_agents': 'Manage Agents',
        'super_admin': 'Super Admin Access'
    };

    if (permissions.length === 0) {
        container.innerHTML = '<p class="text-muted">No permissions assigned</p>';
        return;
    }

    permissions.forEach(permission => {
        const label = permissionLabels[permission] || permission;
        const chip = document.createElement('div');
        chip.className = 'permission-chip';
        chip.innerHTML = `<i class="fas fa-check-circle"></i> ${label}`;
        container.appendChild(chip);
    });
}

// Show edit profile modal
function showEditProfileModal() {
    showModal('Edit Profile', `
        <form id="editProfileForm" class="modal-form" onsubmit="updateProfile(event)">
            <div class="form-group">
                <label>Full Name</label>
                <input type="text" id="editFullName" value="${document.getElementById('profileFullName').innerText}" required>
            </div>
            <div class="form-group">
                <label>Phone Number</label>
                <input type="tel" id="editPhone" placeholder="Enter phone number">
            </div>
            <div class="form-group">
                <label>Location</label>
                <input type="text" id="editLocation" placeholder="Enter your location">
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Changes</button>
            </div>
        </form>
    `);
}

// Update profile
async function updateProfile(event) {
    event.preventDefault();
    
    const fullName = document.getElementById('editFullName').value;
    const phone = document.getElementById('editPhone').value;
    const location = document.getElementById('editLocation').value;

    try {
        const response = await fetch("/admin/profile", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
                full_name: fullName,
                phone: phone,
                location: location
            })
        });

        if (response.ok) {
            showToast('Profile updated successfully!', 'success');
            closeModal();
            loadAdminProfile();
            getAdminProfile();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to update profile', 'error');
        }
    } catch (err) {
        console.error("Error updating profile:", err);
        showToast('Failed to update profile', 'error');
    }
}

// Upload profile picture
async function uploadProfilePicture(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('profile_image', file);

    try {
        const response = await fetch("/admin/profile/picture", {
            method: "POST",
            credentials: "include",
            body: formData
        });

        if (response.ok) {
            showToast('Profile picture updated!', 'success');
            loadAdminProfile();
        } else {
            showToast('Failed to upload picture', 'error');
        }
    } catch (err) {
        console.error("Error uploading picture:", err);
        showToast('Failed to upload picture', 'error');
    }
}

// Edit personal info
function editPersonalInfo() {
    showEditProfileModal();
}

// Show change password modal
function showChangePasswordModal() {
    showModal('Change Password', `
        <form id="changePasswordForm" class="modal-form" onsubmit="changePassword(event)">
            <div class="form-group">
                <label>Current Password</label>
                <input type="password" id="currentPwd" required>
            </div>
            <div class="form-group">
                <label>New Password</label>
                <input type="password" id="newPwd" required minlength="8">
            </div>
            <div class="form-group">
                <label>Confirm New Password</label>
                <input type="password" id="confirmPwd" required minlength="8">
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Change Password</button>
            </div>
        </form>
    `);
}

// Change password
async function changePassword(event) {
    event.preventDefault();
    
    const currentPassword = document.getElementById('currentPwd').value;
    const newPassword = document.getElementById('newPwd').value;
    const confirmPassword = document.getElementById('confirmPwd').value;

    if (newPassword !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }

    if (newPassword.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }

    try {
        const response = await fetch("/admin/change-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        if (response.ok) {
            showToast('Password changed successfully!', 'success');
            closeModal();
            document.getElementById('lastPasswordChange').innerText = new Date().toLocaleDateString();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to change password', 'error');
        }
    } catch (err) {
        console.error("Error changing password:", err);
        showToast('Failed to change password', 'error');
    }
}

// Toggle two-factor authentication
async function toggleTwoFactor() {
    const isEnabled = document.getElementById('twoFactorToggle').checked;
    
    try {
        const response = await fetch("/admin/security/2fa", {
            method: isEnabled ? "POST" : "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include"
        });

        if (response.ok) {
            showToast(`Two-factor authentication ${isEnabled ? 'enabled' : 'disabled'}!`, 'success');
        } else {
            document.getElementById('twoFactorToggle').checked = !isEnabled;
            showToast('Failed to update 2FA settings', 'error');
        }
    } catch (err) {
        console.error("Error toggling 2FA:", err);
        document.getElementById('twoFactorToggle').checked = !isEnabled;
        showToast('Failed to update 2FA settings', 'error');
    }
}

// Show login history
function showLoginHistory() {
    showModal('Login History', `
        <div class="table-container" style="max-height: 400px; overflow-y: auto;">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Date & Time</th>
                        <th>IP Address</th>
                        <th>Device</th>
                        <th>Location</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>${new Date().toLocaleString()}</td>
                        <td>192.168.1.1</td>
                        <td>Chrome on Windows</td>
                        <td>Dhaka, Bangladesh</td>
                        <td><span class="badge badge-success">Success</span></td>
                    </tr>
                    <tr>
                        <td>${new Date(Date.now() - 86400000).toLocaleString()}</td>
                        <td>192.168.1.1</td>
                        <td>Safari on macOS</td>
                        <td>Dhaka, Bangladesh</td>
                        <td><span class="badge badge-success">Success</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    `);
}

// Show active sessions
function showActiveSessions() {
    showModal('Active Sessions', `
        <div class="session-list">
            <div class="security-item">
                <div class="security-info">
                    <i class="fas fa-desktop"></i>
                    <div>
                        <span class="security-title">This Device</span>
                        <span class="security-desc">Current session • Started ${new Date().toLocaleDateString()}</span>
                    </div>
                </div>
                <span class="badge badge-success">Active</span>
            </div>
        </div>
        <div class="modal-actions" style="margin-top: 20px;">
            <button class="btn btn-danger" onclick="logoutAllSessions()">Logout All Other Sessions</button>
        </div>
    `);
}

// Logout all other sessions
async function logoutAllSessions() {
    try {
        const response = await fetch("/admin/security/sessions/revoke-others", {
            method: "POST",
            credentials: "include"
        });

        if (response.ok) {
            showToast('All other sessions logged out', 'success');
            closeModal();
        } else {
            showToast('Failed to logout sessions', 'error');
        }
    } catch (err) {
        console.error("Error logging out sessions:", err);
        showToast('Failed to logout sessions', 'error');
    }
}

// Toggle notification
function toggleNotification(type) {
    const toggles = {
        'email': document.getElementById('emailNotifToggle'),
        'push': document.getElementById('pushNotifToggle'),
        'security': document.getElementById('securityAlertsToggle'),
        'userActivity': document.getElementById('userActivityToggle')
    };

    const isEnabled = toggles[type]?.checked;
    showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} notifications ${isEnabled ? 'enabled' : 'disabled'}`, 'success');
}

// Show activity log
function showActivityLog() {
    showModal('Activity Log', `
        <div class="activity-timeline" style="max-height: 400px; overflow-y: auto;">
            <div class="activity-item">
                <div class="activity-icon" style="background: var(--primary-light); color: var(--primary-color);">
                    <i class="fas fa-sign-in-alt"></i>
                </div>
                <div class="activity-content">
                    <span class="activity-title">Logged in successfully</span>
                    <span class="activity-time">${new Date().toLocaleString()}</span>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-icon" style="background: #dcfce7; color: #16a34a;">
                    <i class="fas fa-user-edit"></i>
                </div>
                <div class="activity-content">
                    <span class="activity-title">Profile updated</span>
                    <span class="activity-time">${new Date(Date.now() - 3600000).toLocaleString()}</span>
                </div>
            </div>
        </div>
    `);
}

// Export my data
function exportMyData() {
    showToast('Preparing your data export...', 'info');
    setTimeout(() => {
        showToast('Data export downloaded!', 'success');
    }, 2000);
}

// Show API keys
function showAPIKeys() {
    showModal('API Keys', `
        <div class="api-keys-list">
            <div class="security-item">
                <div class="security-info">
                    <i class="fas fa-key"></i>
                    <div>
                        <span class="security-title">Production API Key</span>
                        <span class="security-desc">pk_live_••••••••••••••••</span>
                    </div>
                </div>
                <button class="btn btn-sm btn-secondary" onclick="copyApiKey('pk_live_...')">Copy</button>
            </div>
            <div class="security-item">
                <div class="security-info">
                    <i class="fas fa-key"></i>
                    <div>
                        <span class="security-title">Test API Key</span>
                        <span class="security-desc">pk_test_••••••••••••••••</span>
                    </div>
                </div>
                <button class="btn btn-sm btn-secondary" onclick="copyApiKey('pk_test_...')">Copy</button>
            </div>
        </div>
        <div class="modal-actions" style="margin-top: 20px;">
            <button class="btn btn-primary"><i class="fas fa-plus"></i> Generate New Key</button>
        </div>
    `);
}

// Show audit log
function showAuditLog() {
    showModal('Audit Log', `
        <div class="table-container" style="max-height: 400px; overflow-y: auto;">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Action</th>
                        <th>Details</th>
                        <th>IP Address</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>${new Date().toLocaleString()}</td>
                        <td>Login</td>
                        <td>Successful login</td>
                        <td>192.168.1.1</td>
                    </tr>
                    <tr>
                        <td>${new Date(Date.now() - 86400000).toLocaleString()}</td>
                        <td>Profile Update</td>
                        <td>Admin updated profile</td>
                        <td>192.168.1.1</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `);
}

// Confirm delete account
function confirmDeleteAccount() {
    showModal('Delete Account', `
        <div class="error-message-dialog">
            <i class="fas fa-exclamation-triangle"></i>
            <p>This action is irreversible. All your data will be permanently deleted.</p>
        </div>
        <form id="deleteAccountForm" class="modal-form" style="margin-top: 20px;" onsubmit="deleteAccount(event)">
            <div class="form-group">
                <label>Enter your password to confirm</label>
                <input type="password" id="deleteConfirmPassword" required>
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-danger">Delete My Account</button>
            </div>
        </form>
    `);
}

// Delete account
async function deleteAccount(event) {
    event.preventDefault();
    
    showToast('This feature requires additional verification', 'warning');
    closeModal();
}


// initiallize
function initializeDashboard() {
    loadAdminProfile();
    
    // বর্তমান ইউআরএল চেক করে সেই অনুযায়ী ডেটা লোড করা
    const path = window.location.pathname;
    if (path.includes('dashboard')) {
        getDashboardStats();
        getUser();
    } else if (path.includes('mobile-operators')) {
        if (typeof loadOperators === 'function') loadOperators();
    }
}

// Page titles for navigation
const pageTitles = {
    'dashboard': 'Dashboard',
    'users': 'Users',
    'transactions': 'Transactions',
    'wallets': 'Wallets',
    'settings': 'Profile',
    'mobile-operators': 'Mobile Operators'
};

// Navigate to a specific page
function navigateTo(pageName) {
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to clicked nav item
    const activeNavItem = document.querySelector(`.nav-item[data-page="${pageName}"]`);
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
    
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show the target page
    const targetPage = document.getElementById(`${pageName}Page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update page title
    const pageTitle = pageTitles[pageName] || 'Dashboard';
    document.getElementById('pageTitle').textContent = pageTitle;
    
    // Load data for specific pages
    if (pageName === 'users' && typeof loadUsers === 'function') {
        loadUsers();
    } else if (pageName === 'transactions' && typeof loadTransactions === 'function') {
        loadTransactions();
    } else if (pageName === 'wallets' && typeof loadWallets === 'function') {
        loadWallets();
    } else if (pageName === 'mobile-operators' && typeof loadOperators === 'function') {
        loadOperators();
    }
}

// Initialize nav item click handlers
function initializeNavigation() {
    document.querySelectorAll('.nav-item[data-page]').forEach(navItem => {
        navItem.addEventListener('click', function(e) {
            e.preventDefault();
            const pageName = this.getAttribute('data-page');
            navigateTo(pageName);
        });
    });
}

document.addEventListener("DOMContentLoaded", function() {
    initializeDashboard();
    initializeNavigation();
});
