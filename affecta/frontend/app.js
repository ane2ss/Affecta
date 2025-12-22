const API_BASE = '/api';

// --- State ---
let allAffectations = [];
let mainFile = null;
let uniqueCommunes = new Set();
let selectedItems = new Set();

// --- DOM Elements ---
// Navigation
const navItems = document.querySelectorAll('.nav-item');
const tabContents = document.querySelectorAll('.tab-content');

// Affectations
const affectationTableBody = document.querySelector('#affectation-table tbody');
const countDisplay = document.getElementById('count-display');
const affectationUpload = document.getElementById('affectation-upload');
const addBtn = document.getElementById('add-btn');
const filterInput = document.getElementById('filter-affectation');
const exportBtn = document.getElementById('export-btn');
const deleteAllBtn = document.getElementById('delete-all-btn');

// Bulk
const selectAllChk = document.getElementById('select-all-chk');
const bulkBar = document.getElementById('bulk-bar');
const selectedCount = document.getElementById('selected-count');
const bulkCommuneBtn = document.getElementById('bulk-commune-btn');
const bulkDeleteBtn = document.getElementById('bulk-delete-btn');

// Modal
const modal = document.getElementById('modal');
const modalForm = document.getElementById('modal-form');
const closeModalBtn = document.getElementById('close-modal');
const cancelBtn = document.getElementById('cancel-btn');
const inputName = document.getElementById('input-name');
const inputCommune = document.getElementById('input-commune');

// Processing
const dropZone = document.getElementById('drop-zone');
const mainUpload = document.getElementById('main-upload');
const fileInfo = document.getElementById('file-info');
const fileNameDisplay = document.getElementById('file-name');
const removeFileBtn = document.getElementById('remove-file');
const generateBtn = document.getElementById('generate-btn');
const downloadBtn = document.getElementById('download-btn');
const statusMsg = document.getElementById('status-msg');
const generationFilters = document.getElementById('generation-filters');
const communeCheckboxes = document.getElementById('commune-checkboxes');
const selectAllBtn = document.getElementById('select-all-btn');
const deselectAllBtn = document.getElementById('deselect-all-btn');


// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    loadAffectations();
    setupNavigation();
});

// --- Navigation ---
function setupNavigation() {
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active class
            navItems.forEach(n => n.classList.remove('active'));
            tabContents.forEach(t => t.classList.remove('active'));

            // Add active class
            item.classList.add('active');
            const tabId = item.getAttribute('data-tab');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        });
    });
}

// --- Affectation Logic ---

async function loadAffectations() {
    try {
        const res = await fetch(`${API_BASE}/affectations`);
        const data = await res.json();
        allAffectations = data.items;

        // Update unique communes for filtering
        uniqueCommunes = new Set(allAffectations.map(item => item.commune).filter(Boolean));

        selectedItems.clear();
        updateBulkUI();
        renderTable(allAffectations);
        updateCommuneCheckboxes(); // Update processing tab filters
    } catch (err) {
        console.error('Failed to load affectations', err);
    }
}

function renderTable(items) {
    affectationTableBody.innerHTML = '';
    items.forEach(item => {
        const tr = document.createElement('tr');
        const isSelected = selectedItems.has(item.name);
        tr.innerHTML = `
            <td><input type="checkbox" class="row-chk" value="${item.name}" ${isSelected ? 'checked' : ''}></td>
            <td>${item.name}</td>
            <td>${item.commune}</td>
            <td>
                <button class="icon-btn" onclick="editItem('${item.name}', '${item.commune}')" title="Modifier">
                    <span class="material-icons">edit</span>
                </button>
                <button class="icon-btn" onclick="deleteItem('${item.name}')" title="Supprimer">
                    <span class="material-icons">delete</span>
                </button>
            </td>
        `;
        affectationTableBody.appendChild(tr);
    });
    countDisplay.textContent = `${items.length} entrées`;

    // Re-attach checkbox listeners
    document.querySelectorAll('.row-chk').forEach(chk => {
        chk.addEventListener('change', (e) => {
            if (e.target.checked) selectedItems.add(e.target.value);
            else selectedItems.delete(e.target.value);
            updateBulkUI();
        });
    });
}

// Bulk UI
function updateBulkUI() {
    const count = selectedItems.size;
    if (count > 0) {
        bulkBar.classList.remove('hidden');
        selectedCount.textContent = `${count} sélectionné(s)`;
    } else {
        bulkBar.classList.add('hidden');
        selectAllChk.checked = false;
    }
}

selectAllChk.addEventListener('change', (e) => {
    const isChecked = e.target.checked;
    // Only select currently visible items (filtered)
    const visibleRows = document.querySelectorAll('.row-chk');
    visibleRows.forEach(chk => {
        chk.checked = isChecked;
        if (isChecked) selectedItems.add(chk.value);
        else selectedItems.delete(chk.value);
    });
    updateBulkUI();
});

// Filter Affectations
filterInput.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allAffectations.filter(item =>
        item.name.toLowerCase().includes(term) ||
        item.commune.toLowerCase().includes(term)
    );
    renderTable(filtered);
});

// Upload Affectation
affectationUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch(`${API_BASE}/affectations/upload`, {
            method: 'POST',
            body: formData
        });
        const result = await res.json();
        if (result.success) {
            loadAffectations();
            alert(result.message);
        } else {
            alert('Erreur: ' + result.message);
        }
    } catch (err) {
        alert('Erreur upload');
    }
    e.target.value = '';
});

// Export
exportBtn.addEventListener('click', () => {
    window.location.href = `${API_BASE}/affectations/export`;
});

// Delete All
deleteAllBtn.addEventListener('click', async () => {
    if (!confirm('ATTENTION: Vous êtes sur le point de supprimer TOUTES les affectations. Continuer ?')) return;
    try {
        const res = await fetch(`${API_BASE}/affectations/delete-all`, { method: 'DELETE' });
        const result = await res.json();
        if (result.success) {
            loadAffectations();
            alert('Toutes les données ont été supprimées.');
        }
    } catch (err) {
        alert('Erreur lors de la suppression');
    }
});

// Bulk Delete
bulkDeleteBtn.addEventListener('click', async () => {
    if (!confirm(`Supprimer ${selectedItems.size} éléments ?`)) return;
    try {
        const res = await fetch(`${API_BASE}/affectations/bulk-delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(Array.from(selectedItems))
        });
        const result = await res.json();
        if (result.success) {
            loadAffectations();
        }
    } catch (err) {
        alert('Erreur lors de la suppression');
    }
});

// Bulk Update
bulkCommuneBtn.addEventListener('click', async () => {
    const newCommune = prompt("Entrez la nouvelle commune pour les éléments sélectionnés :");
    if (!newCommune) return;

    try {
        const res = await fetch(`${API_BASE}/affectations/bulk-update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                names: Array.from(selectedItems),
                commune: newCommune
            })
        });
        const result = await res.json();
        if (result.success) {
            loadAffectations();
        }
    } catch (err) {
        alert('Erreur lors de la mise à jour');
    }
});

// Delete Item
async function deleteItem(name) {
    if (!confirm(`Supprimer ${name} ?`)) return;
    try {
        await fetch(`${API_BASE}/affectations/delete/${encodeURIComponent(name)}`, { method: 'DELETE' });
        loadAffectations();
    } catch (err) {
        alert('Erreur lors de la suppression');
    }
}
window.deleteItem = deleteItem;

// Edit Item
function editItem(name, commune) {
    inputName.value = name;
    inputCommune.value = commune;
    inputName.readOnly = true;
    inputName.style.backgroundColor = "#f0f0f0";
    inputName.title = "Pour modifier le nom, supprimez et recréez l'entrée.";

    modal.classList.remove('hidden');
}
window.editItem = editItem;

// Modal Logic
function openModal() {
    inputName.value = '';
    inputCommune.value = '';
    inputName.readOnly = false;
    inputName.style.backgroundColor = "white";
    inputName.title = "";
    modal.classList.remove('hidden');
}
function closeModal() {
    modal.classList.add('hidden');
}

addBtn.addEventListener('click', openModal);
closeModalBtn.addEventListener('click', closeModal);
cancelBtn.addEventListener('click', closeModal);

modalForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const item = {
        name: inputName.value,
        commune: inputCommune.value
    };

    try {
        const res = await fetch(`${API_BASE}/affectations/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
        });
        const result = await res.json();
        if (result.success) {
            closeModal();
            loadAffectations();
        }
    } catch (err) {
        alert('Erreur sauvegarde');
    }
});

// --- Processing Logic ---

// Drag & Drop
dropZone.addEventListener('click', (e) => {
    if (e.target !== removeFileBtn && !removeFileBtn.contains(e.target)) {
        mainUpload.click();
    }
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--primary)';
    dropZone.style.background = '#f0fdf4';
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--border)';
    dropZone.style.background = '#fafafa';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--border)';
    dropZone.style.background = '#fafafa';
    if (e.dataTransfer.files.length) {
        handleMainFile(e.dataTransfer.files[0]);
    }
});

mainUpload.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleMainFile(e.target.files[0]);
    }
});

function handleMainFile(file) {
    mainFile = file;
    fileNameDisplay.textContent = file.name;
    fileInfo.classList.remove('hidden');
    generateBtn.disabled = false;
    downloadBtn.classList.add('hidden');
    statusMsg.textContent = '';
    generationFilters.classList.remove('hidden');
}

removeFileBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    mainFile = null;
    mainUpload.value = '';
    fileInfo.classList.add('hidden');
    generateBtn.disabled = true;
    generationFilters.classList.add('hidden');
    statusMsg.textContent = '';
});

// Generation Filters
function updateCommuneCheckboxes() {
    communeCheckboxes.innerHTML = '';
    const sortedCommunes = Array.from(uniqueCommunes).sort();

    sortedCommunes.forEach(commune => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        div.innerHTML = `
            <input type="checkbox" id="chk-${commune}" value="${commune}" checked>
            <label for="chk-${commune}">${commune}</label>
        `;
        communeCheckboxes.appendChild(div);
    });
}

selectAllBtn.addEventListener('click', () => {
    document.querySelectorAll('#commune-checkboxes input').forEach(cb => cb.checked = true);
});

deselectAllBtn.addEventListener('click', () => {
    document.querySelectorAll('#commune-checkboxes input').forEach(cb => cb.checked = false);
});

// Generate
generateBtn.addEventListener('click', async () => {
    if (!mainFile) return;

    // Get selected communes
    const selectedCommunes = Array.from(document.querySelectorAll('#commune-checkboxes input:checked'))
        .map(cb => cb.value);

    if (selectedCommunes.length === 0) {
        alert('Veuillez sélectionner au moins une commune.');
        return;
    }

    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="material-icons spin">refresh</span> Traitement...';
    statusMsg.textContent = 'Traitement en cours...';
    statusMsg.className = 'status-msg';

    const formData = new FormData();
    formData.append('file', mainFile);
    formData.append('communes', selectedCommunes.join(','));

    try {
        const res = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            body: formData
        });
        const result = await res.json();

        if (result.success) {
            statusMsg.textContent = 'Fichiers générés avec succès !';
            statusMsg.className = 'status-msg success';
            downloadBtn.classList.remove('hidden');
            downloadBtn.href = result.download_url;
        } else {
            statusMsg.textContent = 'Erreur: ' + result.message;
            statusMsg.className = 'status-msg error';
        }
    } catch (err) {
        statusMsg.textContent = 'Erreur serveur';
        statusMsg.className = 'status-msg error';
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<span class="material-icons">play_arrow</span> Générer les fichiers';
    }
});
