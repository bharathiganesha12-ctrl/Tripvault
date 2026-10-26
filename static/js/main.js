/**
 * TripVault – Main JavaScript
 * TripVault client-side enhancements.
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ------------------------------------------------------------------ */
  /* 1. Toggle password visibility                                        */
  /* ------------------------------------------------------------------ */
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.closest('.input-group').querySelector('input[type="password"], input[type="text"]');
      const icon  = btn.querySelector('i');
      if (!input) return;
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('bi-eye', 'bi-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('bi-eye-slash', 'bi-eye');
      }
    });
  });

  /* ------------------------------------------------------------------ */
  /* 2. Password strength meter (register page)                          */
  /* ------------------------------------------------------------------ */
  const regPassword = document.getElementById('regPassword');
  const strengthBar  = document.getElementById('passwordStrengthBar');
  const strengthText = document.getElementById('passwordStrengthText');

  if (regPassword && strengthBar) {
    regPassword.addEventListener('input', () => {
      const val = regPassword.value;
      let score = 0;
      if (val.length >= 8)              score++;
      if (/[A-Z]/.test(val))            score++;
      if (/[0-9]/.test(val))            score++;
      if (/[^A-Za-z0-9]/.test(val))    score++;

      strengthBar.className = 'progress-bar';
      if (val.length === 0) {
        strengthBar.style.width = '0%';
        strengthText.textContent = '';
      } else if (score <= 1) {
        strengthBar.classList.add('weak');
        strengthText.textContent = 'Weak – add uppercase, numbers, or symbols';
        strengthText.style.color = '#ef4444';
      } else if (score <= 3) {
        strengthBar.classList.add('medium');
        strengthText.textContent = 'Medium – getting better!';
        strengthText.style.color = '#f59e0b';
      } else {
        strengthBar.classList.add('strong');
        strengthText.textContent = 'Strong password';
        strengthText.style.color = '#22c55e';
      }
    });
  }

  /* ------------------------------------------------------------------ */
  /* 3. Confirm password validation                                      */
  /* ------------------------------------------------------------------ */
  const confirmPassword = document.getElementById('confirmPassword');
  if (regPassword && confirmPassword) {
    confirmPassword.addEventListener('input', () => {
      if (confirmPassword.value !== regPassword.value) {
        confirmPassword.setCustomValidity('Passwords do not match');
      } else {
        confirmPassword.setCustomValidity('');
      }
    });
  }

  /* ------------------------------------------------------------------ */
  /* 4. Destination search & filters (destinations page)                 */
  /* ------------------------------------------------------------------ */
  const destSearch      = document.getElementById('destSearch');
  const continentFilter = document.getElementById('continentFilter');
  const categoryFilter  = document.getElementById('categoryFilter');
  const budgetRange     = document.getElementById('budgetRange');
  const budgetDisplay   = document.getElementById('budgetDisplay');
  const noResults       = document.getElementById('noResults');
  const resultsCount    = document.getElementById('resultsCount');

  function filterDestinations() {
    const searchVal   = (destSearch?.value   || '').toLowerCase();
    const continent   = (continentFilter?.value || '').toLowerCase();
    const category    = (categoryFilter?.value  || '').toLowerCase();
    const maxBudget   = parseInt(budgetRange?.value || 5000);

    const items = document.querySelectorAll('.dest-item');
    let visible = 0;

    items.forEach(item => {
      const name   = (item.dataset.name       || '').toLowerCase();
      const cont   = (item.dataset.continent  || '').toLowerCase();
      const cat    = (item.dataset.category   || '').toLowerCase();
      const price  = parseInt(item.dataset.price || 0);

      const matchSearch    = !searchVal  || name.includes(searchVal);
      const matchContinent = !continent  || cont === continent;
      const matchCategory  = !category   || cat  === category;
      const matchBudget    = price <= maxBudget;

      if (matchSearch && matchContinent && matchCategory && matchBudget) {
        item.style.display = '';
        visible++;
      } else {
        item.style.display = 'none';
      }
    });

    if (noResults)     noResults.classList.toggle('d-none', visible > 0);
    if (resultsCount)  resultsCount.textContent = `Showing ${visible} destination${visible !== 1 ? 's' : ''}`;
  }

  if (destSearch)      destSearch.addEventListener('input',  filterDestinations);
  if (continentFilter) continentFilter.addEventListener('change', filterDestinations);
  if (categoryFilter)  categoryFilter.addEventListener('change',  filterDestinations);

  if (budgetRange && budgetDisplay) {
    budgetRange.addEventListener('input', () => {
      budgetDisplay.textContent = `$${parseInt(budgetRange.value).toLocaleString()}`;
      filterDestinations();
    });
  }

  // Clear filters buttons
  document.querySelectorAll('#clearFilters, #clearFilters2').forEach(btn => {
    btn.addEventListener('click', () => {
      if (destSearch)      destSearch.value = '';
      if (continentFilter) continentFilter.value = '';
      if (categoryFilter)  categoryFilter.value  = '';
      if (budgetRange)     { budgetRange.value = 5000; if (budgetDisplay) budgetDisplay.textContent = '$5,000'; }
      filterDestinations();
    });
  });

  /* ------------------------------------------------------------------ */
  /* 6. Grid / List view toggle (destinations page)                      */
  /* ------------------------------------------------------------------ */
  const gridViewBtn = document.getElementById('gridView');
  const listViewBtn = document.getElementById('listView');
  const destGrid    = document.getElementById('destinationsGrid');

  if (gridViewBtn && listViewBtn && destGrid) {
    gridViewBtn.addEventListener('click', () => {
      destGrid.querySelectorAll('.dest-item').forEach(el => {
        el.className = el.className.replace(/col-\w+-\d+/g, '').trim();
        el.classList.add('col-lg-4', 'col-md-6');
      });
      gridViewBtn.classList.add('active');
      listViewBtn.classList.remove('active');
    });

    listViewBtn.addEventListener('click', () => {
      destGrid.querySelectorAll('.dest-item').forEach(el => {
        el.className = el.className.replace(/col-\w+-\d+/g, '').trim();
        el.classList.add('col-12');
      });
      listViewBtn.classList.add('active');
      gridViewBtn.classList.remove('active');
    });
  }

  /* ------------------------------------------------------------------ */
  /* 7. Wishlist / heart toggle                                          */
  /* ------------------------------------------------------------------ */
  document.querySelectorAll('.tv-wishlist-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const icon = btn.querySelector('i');
      btn.classList.toggle('active');
      if (btn.classList.contains('active')) {
        icon.classList.replace('bi-heart', 'bi-heart-fill');
        icon.style.color = '#e11d48';
      } else {
        icon.classList.replace('bi-heart-fill', 'bi-heart');
        icon.style.color = '';
      }
    });
  });

  /* ------------------------------------------------------------------ */
  /* 8. Document search (documents page)                                 */
  /* ------------------------------------------------------------------ */
  const docSearch = document.getElementById('docSearch');
  if (docSearch) {
    docSearch.addEventListener('input', () => {
      const q = docSearch.value.toLowerCase();
      document.querySelectorAll('.doc-row').forEach(row => {
        row.style.display = (row.dataset.name || '').includes(q) ? '' : 'none';
      });
    });
  }

  // Document category filter
  document.querySelectorAll('[data-filter]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      document.querySelectorAll('.doc-row').forEach(row => {
        row.style.display = (filter === 'all' || row.dataset.type === filter) ? '' : 'none';
      });
    });
  });

  /* ------------------------------------------------------------------ */
  /* 9. Document file input preview                                      */
  /* ------------------------------------------------------------------ */
  const fileInput   = document.getElementById('fileInput');
  const filePreview = document.getElementById('filePreview');
  const filePreviewName = document.getElementById('filePreviewName');
  const clearFile   = document.getElementById('clearFile');

  if (fileInput && filePreview) {
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        const f = fileInput.files[0];
        // 25 MB size check
        if (f.size > 25 * 1024 * 1024) {
          alert('File exceeds the 25 MB limit. Please choose a smaller file.');
          fileInput.value = '';
          return;
        }
        filePreviewName.textContent = `${f.name} (${(f.size / 1024).toFixed(1)} KB)`;
        filePreview.classList.remove('d-none');
      }
    });
    if (clearFile) {
      clearFile.addEventListener('click', () => {
        fileInput.value = '';
        filePreview.classList.add('d-none');
      });
    }
  }

  /* ------------------------------------------------------------------ */
  /* 10. Drag-and-drop zone (documents page)                             */
  /* ------------------------------------------------------------------ */
  const dropZone = document.getElementById('dropZone');
  if (dropZone) {
    ['dragenter', 'dragover'].forEach(evt => {
      dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    });
    ['dragleave', 'drop'].forEach(evt => {
      dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.remove('drag-over'); });
    });
    dropZone.addEventListener('drop', e => {
      // Open upload modal when file is dropped
      const modal = document.getElementById('uploadModal');
      if (modal) new bootstrap.Modal(modal).show();
    });
  }

  /* ------------------------------------------------------------------ */
  /* 11. Booking price calculator                                        */
  /* ------------------------------------------------------------------ */
  const basePrice    = 1299; // fallback
  const numAdults    = document.getElementById('numAdults');
  const numChildren  = document.getElementById('numChildren');
  const basePriceEl  = document.getElementById('basePrice');
  const childPriceEl = document.getElementById('childrenPrice');
  const totalPriceEl = document.getElementById('totalPrice');

  function updatePrice() {
    if (!totalPriceEl) return;
    const adults   = parseInt(numAdults?.value   || 2);
    const children = parseInt(numChildren?.value || 0);
    const adultCost  = adults   * basePrice;
    const childCost  = children * Math.round(basePrice * 0.7);
    const taxes      = 180;
    const total      = adultCost + childCost + taxes;
    if (basePriceEl)  basePriceEl.textContent  = `$${adultCost.toLocaleString()}`;
    if (childPriceEl) childPriceEl.textContent = childCost > 0 ? `$${childCost.toLocaleString()}` : '$0';
    totalPriceEl.textContent = `$${total.toLocaleString()}`;
  }

  if (numAdults)   numAdults.addEventListener('change',   updatePrice);
  if (numChildren) numChildren.addEventListener('change', updatePrice);

  /* ------------------------------------------------------------------ */
  /* 12. Budget range display (destinations page)                        */
  /* ------------------------------------------------------------------ */
  if (budgetRange && budgetDisplay) {
    budgetDisplay.textContent = `$${parseInt(budgetRange.value).toLocaleString()}`;
  }

  /* ------------------------------------------------------------------ */
  /* 13. Admin destination search (admin dashboard)                      */
  /* ------------------------------------------------------------------ */
  const adminSearch = document.getElementById('adminDestSearch');
  if (adminSearch) {
    adminSearch.addEventListener('input', () => {
      const q = adminSearch.value.toLowerCase();
      document.querySelectorAll('.tv-table tbody tr').forEach(row => {
        const txt = row.firstElementChild?.textContent?.toLowerCase() || '';
        row.style.display = txt.includes(q) ? '' : 'none';
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* 14. Set minimum travel date to today                                */
  /* ------------------------------------------------------------------ */
  document.querySelectorAll('#travelDate, #returnDate, #searchDate').forEach(input => {
    input.min = new Date().toISOString().split('T')[0];
  });

  /* ------------------------------------------------------------------ */
  /* 15. Navbar active-link highlight for current page                   */
  /* ------------------------------------------------------------------ */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.tv-navbar .nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) link.classList.add('active');
  });

});
