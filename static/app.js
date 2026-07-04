// IEEE Power Publications Tracker - App Logic

// App State
const state = {
    papers: [],
    totalCount: 0,
    currentPage: 1,
    limit: 15,
    search: '',
    filters: {
        journal: '',
        query_type: '',
        status: ''
    },
    isUpdating: false,
    updatePollInterval: null,
    activePaper: null,
    activeModalTab: 'abstract'
};

// DOM Elements
const elements = {
    statTotal: document.getElementById('stat-total'),
    statEarly: document.getElementById('stat-early'),
    statPf: document.getElementById('stat-pf'),
    statOpf: document.getElementById('stat-opf'),
    
    searchInput: document.getElementById('search-input'),
    btnClearSearch: document.getElementById('btn-clear-search'),
    
    filterJournal: document.getElementById('filter-journal'),
    filterTopic: document.getElementById('filter-topic'),
    filterStatus: document.getElementById('filter-status'),
    
    btnSync: document.getElementById('btn-sync'),
    syncIndicator: document.getElementById('sync-indicator'),
    syncText: document.getElementById('sync-text'),
    syncBtnIcon: document.getElementById('sync-btn-icon'),
    
    updateLogContainer: document.getElementById('update-log-container'),
    updateLogConsole: document.getElementById('update-log-console'),
    progressFill: document.getElementById('progress-fill'),
    btnCloseLog: document.getElementById('btn-close-log'),
    
    resultsCount: document.getElementById('results-count-num'),
    papersList: document.getElementById('papers-list'),
    
    pagination: document.getElementById('pagination'),
    pageNum: document.getElementById('page-num'),
    pageTotal: document.getElementById('page-total'),
    btnPrev: document.getElementById('btn-prev'),
    btnNext: document.getElementById('btn-next'),
    
    lastSyncTime: document.getElementById('last-sync-time'),
    
    // Modal Basic
    paperModal: document.getElementById('paper-modal'),
    modalBackdrop: document.getElementById('modal-backdrop'),
    btnCloseModal: document.getElementById('btn-close-modal'),
    modalJournal: document.getElementById('modal-journal'),
    modalTitle: document.getElementById('modal-title'),
    modalAuthors: document.getElementById('modal-authors'),
    modalDate: document.getElementById('modal-date'),
    modalVolumeIssue: document.getElementById('modal-volume-issue'),
    modalVolumeItem: document.getElementById('modal-volume-item'),
    modalTopic: document.getElementById('modal-topic'),
    modalStatus: document.getElementById('modal-status'),
    modalAbstract: document.getElementById('modal-abstract'),
    modalLinkBtn: document.getElementById('modal-link-btn'),
    modalCopyCitationBtn: document.getElementById('modal-copy-citation-btn'),
    
    // Modal Tab Buttons
    btnModalAbstract: document.getElementById('btn-modal-abstract'),
    btnModalTheory: document.getElementById('btn-modal-theory'),
    btnModalGrid: document.getElementById('btn-modal-grid'),
    btnModalDigest: document.getElementById('btn-modal-digest'),
    
    // Modal Tab Contents
    tabAbstract: document.getElementById('modal-tab-abstract'),
    tabTheory: document.getElementById('modal-tab-theory'),
    tabGrid: document.getElementById('modal-tab-grid'),
    tabDigest: document.getElementById('modal-tab-digest'),
    
    // Curation Placeholders & Results
    theoryNotRun: document.getElementById('theory-not-run'),
    theoryRunning: document.getElementById('theory-running'),
    theoryResult: document.getElementById('theory-result'),
    theoryScore: document.getElementById('theory-score'),
    theoryReviewText: document.getElementById('theory-review-text'),
    
    gridNotRun: document.getElementById('grid-not-run'),
    gridResult: document.getElementById('grid-result'),
    gridScore: document.getElementById('grid-score'),
    gridReviewText: document.getElementById('grid-review-text'),
    
    digestNotRun: document.getElementById('digest-not-run'),
    digestResult: document.getElementById('digest-result'),
    digestText: document.getElementById('digest-text'),
    acronymsList: document.getElementById('acronyms-list'),
    
    btnCuratePaper: document.getElementById('btn-curate-paper'),
    btnCuratePaperGrid: document.getElementById('btn-curate-paper-grid'),
    btnCuratePaperDigest: document.getElementById('btn-curate-paper-digest'),
    
    // Main Navigation Tabs
    navDashboardTab: document.getElementById('nav-dashboard-tab'),
    navTriageTab: document.getElementById('nav-triage-tab'),
    navSimulatorTab: document.getElementById('nav-simulator-tab'),
    triageBadgeCount: document.getElementById('triage-badge-count'),
    
    // Main View Sections
    viewDashboard: document.getElementById('view-dashboard'),
    viewTriage: document.getElementById('view-triage'),
    viewSimulator: document.getElementById('view-simulator'),
    
    // Admin Triage Queue List
    triageList: document.getElementById('triage-list'),
    
    // Simulator Controls & Output
    simCase: document.getElementById('sim-case'),
    simAnalysis: document.getElementById('sim-analysis'),
    btnRunSim: document.getElementById('btn-run-sim'),
    derType: document.getElementById('der-type'),
    derSolar: document.getElementById('der-solar'),
    derBattery: document.getElementById('der-battery'),
    btnRunDer: document.getElementById('btn-run-der'),
    simStatus: document.getElementById('sim-status'),
    simResultsOutput: document.getElementById('sim-results-output')
};

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Render Icons
    lucide.createIcons();
    
    // Load initial data
    loadDashboard();
    checkRunningUpdates();
    fetchTriageCount();
    
    // Setup event listeners
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Main Navigation Tabs
    elements.navDashboardTab.addEventListener('click', () => switchMainTab('dashboard'));
    elements.navTriageTab.addEventListener('click', () => switchMainTab('triage'));
    elements.navSimulatorTab.addEventListener('click', () => switchMainTab('simulator'));

    // Search input with debounce
    let searchDebounceTimer;
    elements.searchInput.addEventListener('input', (e) => {
        state.search = e.target.value.trim();
        
        // Show/hide clear button
        elements.btnClearSearch.style.display = state.search ? 'block' : 'none';
        
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            state.currentPage = 1;
            fetchPapers();
        }, 300);
    });
    
    elements.btnClearSearch.addEventListener('click', () => {
        elements.searchInput.value = '';
        state.search = '';
        elements.btnClearSearch.style.display = 'none';
        state.currentPage = 1;
        fetchPapers();
    });
    
    // Filters
    elements.filterJournal.addEventListener('change', (e) => {
        state.filters.journal = e.target.value;
        state.currentPage = 1;
        fetchPapers();
    });
    
    elements.filterTopic.addEventListener('change', (e) => {
        state.filters.query_type = e.target.value;
        state.currentPage = 1;
        fetchPapers();
    });
    
    elements.filterStatus.addEventListener('change', (e) => {
        state.filters.status = e.target.value;
        state.currentPage = 1;
        fetchPapers();
    });
    
    // Pagination
    elements.btnPrev.addEventListener('click', () => {
        if (state.currentPage > 1) {
            state.currentPage--;
            fetchPapers();
        }
    });
    
    elements.btnNext.addEventListener('click', () => {
        const totalPages = Math.ceil(state.totalCount / state.limit);
        if (state.currentPage < totalPages) {
            state.currentPage++;
            fetchPapers();
        }
    });
    
    // Sync Button
    elements.btnSync.addEventListener('click', triggerManualSync);
    elements.btnCloseLog.addEventListener('click', () => {
        elements.updateLogContainer.style.display = 'none';
    });
    
    // Modal closing events
    elements.btnCloseModal.addEventListener('click', closeModal);
    elements.modalBackdrop.addEventListener('click', closeModal);
    
    // Copy Citation
    elements.modalCopyCitationBtn.addEventListener('click', copyCitationToClipboard);
    
    // Close modal on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && elements.paperModal.classList.contains('active')) {
            closeModal();
        }
    });
    
    // Modal Curation Tab Buttons
    elements.btnModalAbstract.addEventListener('click', () => switchModalTab('abstract'));
    elements.btnModalTheory.addEventListener('click', () => switchModalTab('theory'));
    elements.btnModalGrid.addEventListener('click', () => switchModalTab('grid'));
    elements.btnModalDigest.addEventListener('click', () => switchModalTab('digest'));
    
    // Run Curation Triggers
    const runCurationHandler = () => runCurationPanel(state.activePaper);
    elements.btnCuratePaper.addEventListener('click', runCurationHandler);
    elements.btnCuratePaperGrid.addEventListener('click', runCurationHandler);
    elements.btnCuratePaperDigest.addEventListener('click', runCurationHandler);
    
    // Simulator Actions
    elements.btnRunSim.addEventListener('click', runGridSimulation);
    elements.btnRunDer.addEventListener('click', runDEROptimization);
}

// Switch between Dashboard, Triage, and Simulator tabs
function switchMainTab(tabName) {
    // Nav tabs styling
    elements.navDashboardTab.classList.toggle('active', tabName === 'dashboard');
    elements.navTriageTab.classList.toggle('active', tabName === 'triage');
    elements.navSimulatorTab.classList.toggle('active', tabName === 'simulator');
    
    // Views display
    elements.viewDashboard.style.display = tabName === 'dashboard' ? 'block' : 'none';
    elements.viewTriage.style.display = tabName === 'triage' ? 'block' : 'none';
    elements.viewSimulator.style.display = tabName === 'simulator' ? 'block' : 'none';
    
    if (tabName === 'triage') {
        fetchTriageQueue();
    } else if (tabName === 'dashboard') {
        loadDashboard();
    }
}

// Load Dashboard Info (Stats + Papers)
async function loadDashboard() {
    await fetchStats();
    await fetchPapers();
}

// Check if an update is already running in background
async function checkRunningUpdates() {
    try {
        const response = await fetch('/api/update/status');
        const data = await response.json();
        
        if (data.is_updating) {
            setSyncingState(true);
            showUpdateLogConsole();
            pollUpdateStatus(data.last_update?.id);
        }
    } catch (error) {
        console.error('Error checking running updates:', error);
    }
}

// Fetch Stats from API
async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Failed to fetch statistics.');
        
        const data = await response.json();
        
        // Update Counter values
        elements.statTotal.textContent = data.total;
        elements.statEarly.textContent = data.early_access;
        elements.statPf.textContent = data.power_flow;
        elements.statOpf.textContent = data.optimal_power_flow;
        
        // Update last sync time
        if (data.last_update && data.last_update.completed_at) {
            const date = new Date(data.last_update.completed_at);
            elements.lastSyncTime.textContent = date.toLocaleString();
        } else {
            elements.lastSyncTime.textContent = 'Never';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Fetch Triage Queue Count
async function fetchTriageCount() {
    try {
        const response = await fetch('/api/triage?status=pending');
        const data = await response.json();
        const pendingCount = data.total;
        
        if (pendingCount > 0) {
            elements.triageBadgeCount.textContent = pendingCount;
            elements.triageBadgeCount.style.display = 'inline-flex';
        } else {
            elements.triageBadgeCount.style.display = 'none';
        }
    } catch (error) {
        console.error('Error fetching triage count:', error);
    }
}

// Fetch Papers from API
async function fetchPapers() {
    showPapersLoadingState();
    
    try {
        // Build query string
        const params = new URLSearchParams();
        params.append('limit', state.limit);
        params.append('offset', (state.currentPage - 1) * state.limit);
        
        if (state.search) params.append('search', state.search);
        if (state.filters.journal) params.append('journal', state.filters.journal);
        if (state.filters.query_type) params.append('query_type', state.filters.query_type);
        if (state.filters.status) params.append('status', state.filters.status);
        
        const response = await fetch(`/api/papers?${params.toString()}`);
        if (!response.ok) throw new Error('Failed to fetch publications.');
        
        const data = await response.json();
        state.papers = data.papers;
        state.totalCount = data.total;
        
        renderPapersList();
        renderPagination();
    } catch (error) {
        showPapersErrorState(error.message);
    }
}

// Render Papers List
function renderPapersList() {
    elements.resultsCount.textContent = state.totalCount;
    elements.papersList.innerHTML = '';
    
    if (state.papers.length === 0) {
        elements.papersList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon"><i data-lucide="folder-open"></i></div>
                <h3>No publications found</h3>
                <p>Try modifying your search query or filters.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }
    
    state.papers.forEach(paper => {
        const card = document.createElement('div');
        card.className = 'paper-card';
        card.addEventListener('click', () => openPaperModal(paper));
        
        // Format topic badges
        let topicBadgeHtml = '';
        if (paper.query_type === 'optimal power flow') {
            topicBadgeHtml = '<span class="badge opf">OPF</span>';
        } else if (paper.query_type === 'power flow') {
            topicBadgeHtml = '<span class="badge pf">PF</span>';
        } else {
            topicBadgeHtml = '<span class="badge both">PF & OPF</span>';
        }
        
        // Status Badge
        const statusBadgeClass = paper.status === 'Early Access' ? 'early' : 'published';
        const statusBadgeHtml = `<span class="badge ${statusBadgeClass}">${paper.status}</span>`;
        
        // Format Journal Abbreviation
        let journalAbbr = paper.journal;
        if (paper.journal === 'IEEE Transactions on Power Systems') journalAbbr = 'IEEE Trans. Power Systems (TPWRS)';
        if (paper.journal === 'IEEE Transactions on Power Delivery') journalAbbr = 'IEEE Trans. Power Delivery (TPWRD)';
        if (paper.journal === 'IEEE Transactions on Smart Grid') journalAbbr = 'IEEE Trans. Smart Grid (TSG)';
        
        // Volume / issue display
        const volIssueText = paper.status === 'Published' && paper.volume 
            ? `Vol. ${paper.volume}, No. ${paper.issue}` 
            : 'Early Access Article';
            
        card.innerHTML = `
            <div class="card-top">
                <span class="journal-badge">${journalAbbr}</span>
                <div class="badgelist">
                    ${topicBadgeHtml}
                    ${statusBadgeHtml}
                </div>
            </div>
            <h3 class="paper-title">${escapeHtml(paper.title)}</h3>
            <div class="paper-authors">${escapeHtml(truncateAuthors(paper.authors, 4))}</div>
            <p class="paper-abstract-preview">${escapeHtml(paper.abstract || 'No abstract available in Crossref metadata.')}</p>
            <div class="card-footer">
                <div class="paper-date">
                    <i data-lucide="calendar" style="width: 14px; height: 14px;"></i>
                    <span>${paper.publication_date || 'N/A'}</span>
                </div>
                <div class="paper-issues">${volIssueText}</div>
            </div>
        `;
        
        elements.papersList.appendChild(card);
    });
    
    lucide.createIcons();
}

// Render Pagination Controls
function renderPagination() {
    const totalPages = Math.ceil(state.totalCount / state.limit);
    
    if (totalPages <= 1) {
        elements.pagination.style.display = 'none';
        return;
    }
    
    elements.pagination.style.display = 'flex';
    elements.pageNum.textContent = state.currentPage;
    elements.pageTotal.textContent = totalPages;
    
    elements.btnPrev.disabled = state.currentPage === 1;
    elements.btnNext.disabled = state.currentPage === totalPages;
}

// Show papers loading
function showPapersLoadingState() {
    elements.papersList.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading publications...</p>
        </div>
    `;
}

// Show papers error
function showPapersErrorState(msg) {
    elements.papersList.innerHTML = `
        <div class="empty-state" style="border-color: rgba(239, 68, 68, 0.3);">
            <div class="empty-icon" style="color: #ef4444;"><i data-lucide="alert-triangle"></i></div>
            <h3 style="color: #ef4444;">Failed to load data</h3>
            <p>${msg}</p>
            <button class="btn btn-secondary" onclick="fetchPapers()" style="margin-top: 0.5rem;">Try Again</button>
        </div>
    `;
    lucide.createIcons();
}

// Trigger Manual DB Sync (POST request)
async function triggerManualSync() {
    if (state.isUpdating) return;
    
    setSyncingState(true);
    showUpdateLogConsole();
    elements.updateLogConsole.textContent = "Requesting weekly update from background crawler...\n";
    
    try {
        const response = await fetch('/api/update', { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'started') {
            elements.updateLogConsole.textContent += `Sync successfully started! Task ID log registered.\n`;
            pollUpdateStatus(data.log_id);
        } else {
            elements.updateLogConsole.textContent += `Failed to start sync: ${data.message}\n`;
            setSyncingState(false);
        }
    } catch (error) {
        elements.updateLogConsole.textContent += `Network error: ${error.message}\n`;
        setSyncingState(false);
    }
}

// Poll update status from server
function pollUpdateStatus(logId) {
    if (state.updatePollInterval) clearInterval(state.updatePollInterval);
    
    let progress = 5;
    elements.progressFill.style.width = `${progress}%`;
    
    state.updatePollInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/update/status');
            const data = await response.json();
            
            const log = data.last_update;
            if (!log) return;
            
            // Render console log content
            if (log.log_message) {
                elements.updateLogConsole.textContent = log.log_message;
                // Scroll console to bottom
                elements.updateLogConsole.scrollTop = elements.updateLogConsole.scrollHeight;
            }
            
            // Advance progress bar
            if (progress < 90) {
                progress += 5;
                elements.progressFill.style.width = `${progress}%`;
            }
            
            // Check if finished
            if (!data.is_updating) {
                clearInterval(state.updatePollInterval);
                state.updatePollInterval = null;
                setSyncingState(false);
                
                elements.progressFill.style.width = '100%';
                
                if (log.status === 'completed') {
                    elements.updateLogConsole.textContent += `\n\n=== SYNC SUCCESSFUL ===\n`;
                    elements.updateLogConsole.textContent += `Checked ${log.papers_checked} papers. Added ${log.papers_added} new papers, updated ${log.papers_updated}.`;
                    // Refresh data
                    loadDashboard();
                } else {
                    elements.updateLogConsole.textContent += `\n\n=== SYNC FAILED ===\nError details are shown in the log above.`;
                }
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 2000);
}

// Set UI State to Syncing / Idle
function setSyncingState(isUpdating) {
    state.isUpdating = isUpdating;
    
    if (isUpdating) {
        elements.btnSync.disabled = true;
        elements.syncIndicator.className = 'sync-indicator running';
        elements.syncText.textContent = 'Syncing...';
        elements.syncBtnIcon.classList.add('spin');
    } else {
        elements.btnSync.disabled = false;
        elements.syncIndicator.className = 'sync-indicator idle';
        elements.syncText.textContent = 'System Ready';
        elements.syncBtnIcon.classList.remove('spin');
    }
}

// Show update console in UI
function showUpdateLogConsole() {
    elements.updateLogContainer.style.display = 'block';
    elements.updateLogConsole.textContent = "Loading console logs...";
    elements.progressFill.style.width = '2%';
}

// Switch tabs inside paper modal
function switchModalTab(tabId) {
    state.activeModalTab = tabId;
    
    // Style buttons
    elements.btnModalAbstract.classList.toggle('active', tabId === 'abstract');
    elements.btnModalTheory.classList.toggle('active', tabId === 'theory');
    elements.btnModalGrid.classList.toggle('active', tabId === 'grid');
    elements.btnModalDigest.classList.toggle('active', tabId === 'digest');
    
    // Display sections
    elements.tabAbstract.style.display = tabId === 'abstract' ? 'block' : 'none';
    elements.tabTheory.style.display = tabId === 'theory' ? 'block' : 'none';
    elements.tabGrid.style.display = tabId === 'grid' ? 'block' : 'none';
    elements.tabDigest.style.display = tabId === 'digest' ? 'block' : 'none';
}

// Open Paper Details Modal
async function openPaperModal(paper) {
    state.activePaper = paper;
    
    elements.modalJournal.textContent = paper.journal;
    elements.modalTitle.textContent = paper.title;
    elements.modalAuthors.textContent = paper.authors;
    elements.modalDate.textContent = paper.publication_date || 'Unknown Date';
    
    // Volume & issue
    if (paper.status === 'Published' && paper.volume) {
        elements.modalVolumeIssue.textContent = `Volume ${paper.volume}, Issue ${paper.issue}`;
        elements.modalVolumeItem.style.display = 'flex';
    } else {
        elements.modalVolumeItem.style.display = 'none';
    }
    
    // Topic Tag
    elements.modalTopic.className = 'meta-value badge';
    if (paper.query_type === 'optimal power flow') {
        elements.modalTopic.textContent = 'Optimal Power Flow';
        elements.modalTopic.classList.add('opf');
    } else if (paper.query_type === 'power flow') {
        elements.modalTopic.textContent = 'Power Flow';
        elements.modalTopic.classList.add('pf');
    } else {
        elements.modalTopic.textContent = 'Power Flow & OPF';
        elements.modalTopic.classList.add('both');
    }
    
    // Status Tag
    elements.modalStatus.className = 'meta-value badge';
    if (paper.status === 'Early Access') {
        elements.modalStatus.textContent = 'Early Access';
        elements.modalStatus.classList.add('early');
    } else {
        elements.modalStatus.textContent = 'Published';
        elements.modalStatus.classList.add('published');
    }
    
    // Abstract
    elements.modalAbstract.textContent = paper.abstract || 'No abstract is available for this paper in Crossref metadata.';
    
    // Actions
    elements.modalLinkBtn.href = paper.url;
    
    // Fetch and Load Reviews
    switchModalTab('abstract');
    await loadPaperReview(paper.id);
    
    // Show Modal
    elements.paperModal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Lock background scrolling
}

// Fetch and load review from backend
async function loadPaperReview(paperId) {
    // Reset view states
    showCurationNotRun();
    
    try {
        const response = await fetch(`/api/papers/${paperId}/review`);
        const data = await response.json();
        
        if (data.status === 'success' && data.review) {
            renderReviewData(data.review);
        }
    } catch (error) {
        console.error('Error fetching paper review:', error);
    }
}

// Show "Curation Not Run" state inside tabs
function showCurationNotRun() {
    elements.theoryNotRun.style.display = 'flex';
    elements.theoryRunning.style.display = 'none';
    elements.theoryResult.style.display = 'none';
    
    elements.gridNotRun.style.display = 'flex';
    elements.gridResult.style.display = 'none';
    
    elements.digestNotRun.style.display = 'flex';
    elements.digestResult.style.display = 'none';
}

// Show "Curation Running" loading state
function showCurationRunning() {
    elements.theoryNotRun.style.display = 'none';
    elements.theoryRunning.style.display = 'flex';
    elements.theoryResult.style.display = 'none';
    
    elements.gridNotRun.style.display = 'none';
    elements.gridResult.style.display = 'none';
    
    elements.digestNotRun.style.display = 'none';
    elements.digestResult.style.display = 'none';
}

// Render Review Data
function renderReviewData(review) {
    elements.theoryNotRun.style.display = 'none';
    elements.theoryRunning.style.display = 'none';
    elements.theoryResult.style.display = 'block';
    
    elements.gridNotRun.style.display = 'none';
    elements.gridResult.style.display = 'block';
    
    elements.digestNotRun.style.display = 'none';
    elements.digestResult.style.display = 'block';
    
    // Theory Card
    elements.theoryScore.textContent = `${review.theory_score}/10`;
    elements.theoryReviewText.innerHTML = formatMarkdown(review.theory_review);
    
    // Grid Card
    elements.gridScore.textContent = `${review.grid_score}/10`;
    elements.gridReviewText.innerHTML = formatMarkdown(review.grid_review);
    
    // Digest Card
    elements.digestText.innerHTML = formatMarkdown(review.educational_digest);
    
    // Acronyms List
    elements.acronymsList.innerHTML = '';
    if (review.key_acronyms) {
        try {
            const acronyms = JSON.parse(review.key_acronyms);
            Object.keys(acronyms).forEach(key => {
                const item = document.createElement('div');
                item.className = 'acronym-item';
                item.innerHTML = `<strong>${escapeHtml(key)}</strong>: ${escapeHtml(acronyms[key])}`;
                elements.acronymsList.appendChild(item);
            });
        } catch (e) {
            console.error('Error parsing key acronyms:', e);
        }
    }
}

// Trigger Multi-Agent Curation (POST request)
async function runCurationPanel(paper) {
    if (!paper) return;
    
    showCurationRunning();
    switchModalTab('theory'); // Focus on theory during curation
    
    try {
        const response = await fetch(`/api/papers/${paper.id}/curate`, { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success' && data.review) {
            renderReviewData(data.review);
        } else {
            alert(`Curation failed: ${data.message}`);
            showCurationNotRun();
        }
    } catch (error) {
        console.error('Curation request failed:', error);
        alert(`Error triggering curation: ${error.message}`);
        showCurationNotRun();
    }
}

// Close Paper Details Modal
function closeModal() {
    elements.paperModal.classList.remove('active');
    document.body.style.overflow = ''; // Unlock background scrolling
    state.activePaper = null;
    elements.modalCopyCitationBtn.innerHTML = '<i data-lucide="copy"></i><span>Copy Citation</span>';
    lucide.createIcons();
}

// Copy Citation Helper
function copyCitationToClipboard() {
    if (!state.activePaper) return;
    
    const paper = state.activePaper;
    const year = paper.publication_date ? paper.publication_date.split('-')[0] : 'n.d.';
    
    let citation = `${paper.authors}, "${paper.title}," in *${paper.journal}*`;
    if (paper.status === 'Published' && paper.volume) {
        citation += `, vol. ${paper.volume}, no. ${paper.issue}, ${year}.`;
    } else {
        citation += `, early access online, ${year}.`;
    }
    citation += ` DOI: ${paper.doi}`;
    
    navigator.clipboard.writeText(citation).then(() => {
        elements.modalCopyCitationBtn.innerHTML = '<i data-lucide="check" style="color: #10b981;"></i><span style="color: #10b981;">Copied!</span>';
        lucide.createIcons();
        setTimeout(() => {
            if (state.activePaper === paper) {
                elements.modalCopyCitationBtn.innerHTML = '<i data-lucide="copy"></i><span>Copy Citation</span>';
                lucide.createIcons();
            }
        }, 3000);
    }).catch(err => {
        console.error('Failed to copy citation:', err);
    });
}

// Fetch Admin Triage Queue items
async function fetchTriageQueue() {
    elements.triageList.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Loading triage items...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/triage?status=pending');
        const data = await response.json();
        
        elements.triageList.innerHTML = '';
        
        if (data.papers.length === 0) {
            elements.triageList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i data-lucide="check-circle-2" style="color: var(--accent-teal);"></i></div>
                    <h3>Triage queue is empty</h3>
                    <p>No flagged papers require manual intervention.</p>
                </div>
            `;
            lucide.createIcons();
            fetchTriageCount();
            return;
        }
        
        data.papers.forEach(item => {
            const row = document.createElement('div');
            row.className = 'triage-card';
            row.innerHTML = `
                <div class="triage-card-header">
                    <span class="badge badge-warning">FLAGGED: ${escapeHtml(item.flag_reason)}</span>
                    <span class="triage-date">${new Date(item.flagged_at).toLocaleString()}</span>
                </div>
                <h3 class="triage-title">${escapeHtml(item.title)}</h3>
                <div class="triage-authors"><strong>Authors:</strong> ${escapeHtml(item.authors)}</div>
                <div class="triage-evidence">
                    <strong>Flagged Snippet/Evidence:</strong>
                    <pre>${escapeHtml(item.evidence)}</pre>
                </div>
                <div class="triage-abstract-preview">
                    <strong>Abstract Preview:</strong>
                    <p>${escapeHtml(item.abstract || 'No abstract.')}</p>
                </div>
                <div class="triage-actions">
                    <button class="btn btn-primary" onclick="approveTriageItem(${item.id})">
                        <i data-lucide="check"></i> Approve Ingestion
                    </button>
                    <button class="btn btn-secondary btn-danger" onclick="rejectTriageItem(${item.id})">
                        <i data-lucide="x"></i> Reject Paper
                    </button>
                </div>
            `;
            elements.triageList.appendChild(row);
        });
        
        lucide.createIcons();
        fetchTriageCount();
    } catch (e) {
        elements.triageList.innerHTML = `
            <div class="empty-state" style="border-color: rgba(239, 68, 68, 0.3);">
                <div class="empty-icon" style="color: #ef4444;"><i data-lucide="alert-triangle"></i></div>
                <h3 style="color: #ef4444;">Failed to load triage items</h3>
                <p>${e.message}</p>
            </div>
        `;
        lucide.createIcons();
    }
}

// Approve Triage Ingestion
async function approveTriageItem(id) {
    if (!confirm("Are you sure you want to approve this paper? It will be moved to the main database.")) return;
    
    try {
        const response = await fetch(`/api/triage/${id}/approve`, { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            fetchTriageQueue();
            fetchTriageCount();
        } else {
            alert(`Approval failed: ${data.message}`);
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

// Reject Triage
async function rejectTriageItem(id) {
    if (!confirm("Are you sure you want to reject and discard this paper?")) return;
    
    try {
        const response = await fetch(`/api/triage/${id}/reject`, { method: 'POST' });
        const data = await response.json();
        if (data.status === 'success') {
            fetchTriageQueue();
            fetchTriageCount();
        } else {
            alert(`Rejection failed: ${data.message}`);
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

// Run Power Flow simulation
async function runGridSimulation() {
    const caseId = elements.simCase.value;
    const analysisType = elements.simAnalysis.value;
    
    setSimStatus('Running...', 'running');
    elements.simResultsOutput.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Executing PowerPython solver on IEEE Case ${caseId}...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/simulate/power-flow', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ case_id: caseId, analysis_type: analysisType })
        });
        
        const data = await response.json();
        
        if (data.success) {
            setSimStatus('Success', 'success');
            renderSimResults(data);
        } else {
            setSimStatus('Failed', 'failed');
            renderSimError(data.stdout || data.error);
        }
    } catch (e) {
        setSimStatus('Error', 'failed');
        renderSimError(e.message);
    }
}

// Run Solar BESS Smart Building Optimization
async function runDEROptimization() {
    const buildingType = elements.derType.value;
    const solarCap = parseFloat(elements.derSolar.value);
    const batteryCap = parseFloat(elements.derBattery.value);
    
    setSimStatus('Running...', 'running');
    elements.simResultsOutput.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Solving Building solar-battery charging curves (CVXPY)...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/simulate/solar-building', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                building_type: buildingType,
                solar_cap: solarCap,
                battery_cap: batteryCap,
                days: 1
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            setSimStatus('Success', 'success');
            renderDERResults(data);
        } else {
            setSimStatus('Failed', 'failed');
            renderSimError(data.stdout || data.error);
        }
    } catch (e) {
        setSimStatus('Error', 'failed');
        renderSimError(e.message);
    }
}

function setSimStatus(text, className) {
    elements.simStatus.textContent = text;
    elements.simStatus.className = `sim-status-badge ${className}`;
}

function renderSimResults(results) {
    let outputHtml = `
        <div class="results-stdout">
            <h4>Solver Console Output:</h4>
            <pre>${escapeHtml(results.stdout)}</pre>
        </div>
    `;
    
    // If we have parsed bus results, render them in a clean table
    if (results.data && results.data.bus) {
        outputHtml += `
            <div class="results-table-container">
                <h4>Grid State Profiles (Voltages & Load Angle)</h4>
                <table class="sim-data-table">
                    <thead>
                        <tr>
                            <th>Bus ID</th>
                            <th>VM (p.u.)</th>
                            <th>VA (deg)</th>
                            <th>Active Load (MW)</th>
                            <th>Reactive Load (MVAr)</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.data.bus.map(b => `
                            <tr>
                                <td>${escapeHtml(String(b.Bus_ID))}</td>
                                <td class="${b.VM_pu < 0.95 || b.VM_pu > 1.05 ? 'warning-text' : 'normal-text'}">${parseFloat(b.VM_pu).toFixed(4)}</td>
                                <td>${parseFloat(b.VA_deg).toFixed(2)}</td>
                                <td>${parseFloat(b.PD_MW).toFixed(2)}</td>
                                <td>${parseFloat(b.QD_MVAr).toFixed(2)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    elements.simResultsOutput.innerHTML = outputHtml;
}

function renderDERResults(results) {
    elements.simResultsOutput.innerHTML = `
        <div class="results-stdout">
            <h4>Optimization Dispatch Output (pvlib & CVXPY):</h4>
            <pre>${escapeHtml(results.stdout)}</pre>
        </div>
        <div class="results-der-summary">
            <div class="alert-box success">
                <i data-lucide="check-circle"></i>
                <div>
                    <strong>Optimization Completed Successfully!</strong>
                    <p>Smart building battery charging profile has been generated, minimizing time-of-use costs and peak grid import.</p>
                </div>
            </div>
        </div>
    `;
    lucide.createIcons();
}

function renderSimError(err) {
    elements.simResultsOutput.innerHTML = `
        <div class="empty-state" style="border-color: rgba(239, 68, 68, 0.3);">
            <div class="empty-icon" style="color: #ef4444;"><i data-lucide="alert-triangle"></i></div>
            <h3 style="color: #ef4444;">Simulation Execution Failed</h3>
            <p>${escapeHtml(err || 'Check solver constraints or network convergence parameters.')}</p>
        </div>
    `;
    lucide.createIcons();
}

// Simple Markdown to HTML Formatter
function formatMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/### (.*)/g, '<h4>$1</h4>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/- (.*)/g, '<li>$1</li>')
        .replace(/\n\n/g, '<br><br>');
}

// HTML Escaping Utility
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Truncate author list to prevent card clutter
function truncateAuthors(authorsStr, maxCount = 3) {
    if (!authorsStr) return '';
    const list = authorsStr.split(',');
    if (list.length <= maxCount) return authorsStr;
    
    return list.slice(0, maxCount).join(',') + ` et al.`;
}

// Expose triage button handlers globally for onclick attributes
window.approveTriageItem = approveTriageItem;
window.rejectTriageItem = rejectTriageItem;
