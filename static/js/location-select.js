/**
 * Location Select - Dynamic District Loading
 * دليل الإسماعيلية
 */

// Get CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');


/**
 * تحميل الأحياء حسب المحافظة
 */
function loadDistricts(governorateId, targetSelectId = 'id_district', selectedValue = null) {
    const districtSelect = document.getElementById(targetSelectId);
    
    if (!districtSelect) {
        console.warn('District select not found:', targetSelectId);
        return;
    }
    
    if (!governorateId) {
        districtSelect.innerHTML = '<option value="">اختر المحافظة أولاً</option>';
        districtSelect.disabled = true;
        return;
    }
    
    // Loading state
    districtSelect.innerHTML = '<option value="">جاري التحميل...</option>';
    districtSelect.disabled = true;
    
    // Fetch districts
    fetch(`/api/districts/${governorateId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                districtSelect.innerHTML = '<option value="">اختر الحي</option>';
                
                data.districts.forEach(district => {
                    const option = document.createElement('option');
                    option.value = district.id;
                    option.textContent = district.name;
                    
                    if (selectedValue && district.id == selectedValue) {
                        option.selected = true;
                    }
                    
                    districtSelect.appendChild(option);
                });
                
                districtSelect.disabled = false;
            } else {
                districtSelect.innerHTML = '<option value="">خطأ في التحميل</option>';
                console.error('API Error:', data.error);
            }
        })
        .catch(error => {
            console.error('Fetch Error:', error);
            districtSelect.innerHTML = '<option value="">خطأ في الاتصال</option>';
        });
}


/**
 * تهيئة عند تحميل الصفحة
 */
document.addEventListener('DOMContentLoaded', function() {
    
    // ========== Forms ==========
    const govSelect = document.getElementById('id_governorate');
    const districtSelect = document.getElementById('id_district');
    
    if (govSelect && districtSelect) {
        // Event: Governorate change
        govSelect.addEventListener('change', function() {
            loadDistricts(this.value, 'id_district');
        });
        
        // Initial load (for edit forms)
        if (govSelect.value) {
            const currentDistrict = districtSelect.value;
            loadDistricts(govSelect.value, 'id_district', currentDistrict);
        }
    }
    
    
    // ========== Search Filters ==========
    const filterGov = document.getElementById('filter_governorate');
    const filterDistrict = document.getElementById('filter_district');
    
    if (filterGov && filterDistrict) {
        filterGov.addEventListener('change', function() {
            loadDistricts(this.value, 'filter_district');
        });
        
        // Initial load
        if (filterGov.value) {
            const currentDistrict = filterDistrict.value;
            loadDistricts(filterGov.value, 'filter_district', currentDistrict);
        }
    }
    
    
    // ========== Search Governorate (business list) ==========
    const searchGov = document.getElementById('search_governorate');
    const searchDistrict = document.getElementById('search_district');
    
    if (searchGov && searchDistrict) {
        searchGov.addEventListener('change', function() {
            loadDistricts(this.value, 'search_district');
        });
        
        if (searchGov.value) {
            loadDistricts(searchGov.value, 'search_district');
        }
    }
});
