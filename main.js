// ==============================================================================
// DecoraAI — AI INTERIOR DESIGN ENGINE CLIENT JAVASCRIPT
// ==============================================================================

// Global State
let currentHouseId = null;
let currentHouseData = null;
let currentRoomId = null;
let currentRoomData = null;
let currentDesignId = null;

// ==============================================================================
// NAVBAR & ANIMATIONS
// ==============================================================================
window.addEventListener("scroll", () => {
    const navbar = document.querySelector(".navbar");
    if (!navbar) return;
    if (window.scrollY > 50) {
        navbar.style.boxShadow = "0 10px 40px rgba(0,0,0,.3)";
    } else {
        navbar.style.boxShadow = "none";
    }
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({ behavior: "smooth" });
        }
    });
});

const faqButtons = document.querySelectorAll(".faq-btn");
faqButtons.forEach(button => {
    button.addEventListener("click", () => {
        button.parentElement.classList.toggle("active");
    });
});

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("show");
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll(".feature-card, .gallery-card, .testimonial, .member, .step, .stat-card").forEach(el => {
    el.classList.add("hidden");
    observer.observe(el);
});

// Typing Effect Hero
const words = [
    "Minimalist Living Room",
    "Luxury Penthouse",
    "Scandinavian Kitchen",
    "Modern Home Office",
    "Japandi Bedroom"
];

let wordIndex = 0;
let charIndex = 0;
const heroInput = document.querySelector(".prompt-box input");

function typeText() {
    if (!heroInput || document.activeElement === heroInput || heroInput.value.length > 0) return;
    heroInput.placeholder = words[wordIndex].substring(0, charIndex++);
    if (charIndex > words[wordIndex].length) {
        setTimeout(() => {
            charIndex = 0;
            wordIndex = (wordIndex + 1) % words.length;
        }, 1500);
    }
}

if (heroInput) {
    setInterval(typeText, 120);
    heroInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            generateImage();
        }
    });
}

document.querySelectorAll(".tags span").forEach(tag => {
    tag.style.cursor = "pointer";
    tag.addEventListener("click", () => {
        if (heroInput) {
            heroInput.value = tag.innerText.trim();
            heroInput.focus();
        }
    });
});

// Connect Primary CTA to Studio Modal
document.querySelectorAll(".primary-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        openHouseStudio();
    });
});

// ==============================================================================
// QUICK GENERATE ON HOMEPAGE
// ==============================================================================
async function generateImage() {
    const promptInput = document.querySelector(".prompt-box input");
    const imageElement = document.getElementById("generated-image");
    const generateBtn = document.querySelector(".prompt-box button");
    const prompt = promptInput ? promptInput.value.trim() : "";

    if (!prompt) {
        alert("Please enter a room description prompt.");
        if (promptInput) promptInput.focus();
        return;
    }

    const originalText = generateBtn ? generateBtn.innerHTML : "Generate";
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.innerHTML = "✨ Generating...";
        generateBtn.style.opacity = "0.7";
    }

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();
        if (!response.ok || data.error) {
            alert("Generation Info: " + (data.error || "Server error"));
            return;
        }

        if (imageElement) {
            imageElement.src = data.image;
            imageElement.style.display = "block";
            imageElement.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    } catch (err) {
        console.error("Quick generate failed:", err);
        alert("Could not reach backend server.");
    } finally {
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = originalText;
            generateBtn.style.opacity = "1";
        }
    }
}

// ==============================================================================
// AI HOUSE DESIGN STUDIO (LEVEL 1 & LEVEL 2)
// ==============================================================================

function openHouseStudio() {
    const modal = document.getElementById("house-studio-modal");
    if (modal) {
        modal.classList.add("active");
        loadHouseProjects();
    }
}

function closeHouseStudio() {
    const modal = document.getElementById("house-studio-modal");
    if (modal) modal.classList.remove("active");
}

function switchStudioTab(tabId) {
    document.querySelectorAll(".studio-tab-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(tc => tc.classList.remove("active"));

    const targetTab = document.getElementById(`tab-${tabId}`);
    if (targetTab) targetTab.classList.add("active");

    const activeBtn = Array.from(document.querySelectorAll(".studio-tab-btn")).find(b => b.innerText.toLowerCase().includes(tabId.replace("-", " ")));
    if (activeBtn) activeBtn.classList.add("active");

    if (tabId === 'cost') {
        loadHouseCostTab();
    }
}

async function loadHouseProjects() {
    try {
        const res = await fetch("/api/houses");
        const data = await res.json();
        const select = document.getElementById("active-house-select");
        select.innerHTML = "";

        if (!data.houses || data.houses.length === 0) {
            // Auto create starter project
            const createRes = await fetch("/api/house/create", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: "My Dream Home",
                    total_budget: 1500000,
                    approx_area_sqft: 1600,
                    primary_style: "Modern Luxury"
                })
            });
            const starter = await createRes.json();
            currentHouseId = starter.house.id;
            loadHouseProjects();
            return;
        }

        data.houses.forEach(h => {
            const opt = document.createElement("option");
            opt.value = h.id;
            opt.textContent = `${h.name} (₹${(h.total_budget || 0).toLocaleString('en-IN')})`;
            select.appendChild(opt);
        });

        if (!currentHouseId && data.houses.length > 0) {
            currentHouseId = data.houses[0].id;
        }

        select.value = currentHouseId;
        loadActiveHouseDetails();
    } catch (e) {
        console.error("Failed to load house projects:", e);
    }
}

function onHouseProjectChange() {
    const select = document.getElementById("active-house-select");
    currentHouseId = parseInt(select.value, 10);
    loadActiveHouseDetails();
}

async function deleteActiveHouseProject() {
    if (!currentHouseId) return;
    const projectName = currentHouseData ? currentHouseData.name : "this project";
    if (!confirm(`Are you sure you want to delete "${projectName}"? This will remove all its rooms and generated designs.`)) {
        return;
    }

    try {
        const res = await fetch(`/api/house/${currentHouseId}`, { method: "DELETE" });
        const data = await res.json();
        if (data.status === "success") {
            currentHouseId = null;
            loadHouseProjects();
        } else {
            alert(data.error || "Failed to delete project");
        }
    } catch (e) {
        console.error("Delete house error:", e);
    }
}

async function loadActiveHouseDetails() {
    if (!currentHouseId) return;

    try {
        const res = await fetch(`/api/house/${currentHouseId}`);
        const data = await res.json();
        currentHouseData = data.house;

        // 1. Render House Profile Card
        const pDetails = document.getElementById("house-profile-details");
        const profile = currentHouseData.style_profile || {};
        const palette = (profile.main_palette || []).map(c => `<span class="swatch-pill">${c}</span>`).join(" ");

        pDetails.innerHTML = `
            <div style="margin-bottom:8px;"><strong>House Name:</strong> ${currentHouseData.name}</div>
            <div style="margin-bottom:8px;"><strong>Total Budget:</strong> ₹${(currentHouseData.total_budget || 0).toLocaleString('en-IN')}</div>
            <div style="margin-bottom:8px;"><strong>Total Area:</strong> ${currentHouseData.approx_area_sqft} sq.ft (${currentHouseData.floors} Floor${currentHouseData.floors > 1 ? 's' : ''})</div>
            <div style="margin-bottom:8px;"><strong>Unified Style:</strong> <span style="color:#a78bfa; font-weight:600;">${profile.primary_style || 'Modern Luxury'}</span></div>
            <div style="margin-bottom:8px;"><strong>Color Palette:</strong> <div class="swatch-group">${palette}</div></div>
            <div style="margin-bottom:8px;"><strong>Flooring Spec:</strong> ${profile.flooring_spec || 'Italian Marble'}</div>
            <div><strong>Lighting Temperature:</strong> ${profile.lighting_temp || 'Warm White (3000K)'}</div>
        `;

        // 2. Render Rooms Grid
        const grid = document.getElementById("rooms-grid");
        grid.innerHTML = "";

        const roomSelect = document.getElementById("room-studio-select");
        roomSelect.innerHTML = "";

        (currentHouseData.rooms || []).forEach(r => {
            // Option in room select
            const opt = document.createElement("option");
            opt.value = r.id;
            opt.textContent = `${r.name} (${r.dimensions.length_ft}x${r.dimensions.width_ft} ft)`;
            roomSelect.appendChild(opt);

            // Card in grid
            const card = document.createElement("div");
            card.className = "room-card";
            card.onclick = () => openRoomStudio(r.id);

            const imgCount = r.images_count || (r.images ? r.images.length : 0);
            const imagePreviewHtml = r.latest_design_image ? `
                <div style="position:relative; margin-bottom:12px;">
                    <img src="${r.latest_design_image}" style="width:100%; height:130px; object-fit:cover; border-radius:12px; border:1px solid rgba(255,255,255,0.15);">
                    <span style="position:absolute; top:8px; right:8px; background:rgba(16,185,129,0.85); backdrop-filter:blur(6px); color:white; font-size:10px; font-weight:600; padding:2px 8px; border-radius:12px;">✨ Design Ready</span>
                </div>
            ` : '';

            card.innerHTML = `
                ${imagePreviewHtml}
                <div class="room-card-header">
                    <h5 style="font-size:15px; color:white;">${r.name}</h5>
                    <span class="room-badge">${r.room_type.replace('_', ' ')}</span>
                </div>
                <p style="font-size:12px; color:#94a3b8; margin-bottom:12px;">
                    Dimensions: ${r.dimensions.length_ft} x ${r.dimensions.width_ft} ft (${r.dimensions.area_sqft} sq.ft)
                </p>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:12px; color:#64748b;">
                    <span>📸 ${imgCount} Photo${imgCount === 1 ? '' : 's'}</span>
                    <span style="color:#818cf8; font-weight:600;">Open Studio &rarr;</span>
                </div>
            `;
            grid.appendChild(card);
        });

        // Set active room
        if (currentHouseData.rooms && currentHouseData.rooms.length > 0) {
            if (!currentRoomId || !currentHouseData.rooms.find(r => r.id === currentRoomId)) {
                currentRoomId = currentHouseData.rooms[0].id;
            }
            roomSelect.value = currentRoomId;
            loadActiveRoomStudio();
        }

        // 3. Load Whole House Designs if any
        await loadWholeHouseDesigns();
    } catch (e) {
        console.error("Failed to load house details:", e);
    }
}

async function loadWholeHouseDesigns() {
    if (!currentHouseId) return;
    try {
        const res = await fetch(`/api/house/${currentHouseId}/designs`);
        const data = await res.json();
        const section = document.getElementById("whole-house-designs-section");
        const gallery = document.getElementById("whole-house-gallery");
        const countBadge = document.getElementById("whole-house-designs-count");

        if (data.designs && data.designs.length > 0) {
            section.style.display = "block";
            if (countBadge) countBadge.innerText = `${data.designs.length} Design${data.designs.length === 1 ? '' : 's'}`;
            gallery.innerHTML = "";
            data.designs.forEach(d => {
                const card = document.createElement("div");
                card.className = "glass-card";
                card.style.cssText = "padding:14px; display:flex; flex-direction:column; justify-content:space-between;";
                card.innerHTML = `
                    <div>
                        <img src="${d.image_url}" style="width:100%; height:190px; object-fit:cover; border-radius:12px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.1);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <h5 style="font-size:15px; color:white;">${d.title}</h5>
                        </div>
                        <p style="font-size:11px; color:#94a3b8; line-height:1.5; margin-bottom:12px;">
                            ${d.explanation ? d.explanation.substring(0, 130) + '...' : 'Unified architectural design.'}
                        </p>
                    </div>
                    <button class="btn-secondary" style="width:100%; font-size:12px; padding:8px;" onclick="openRoomStudio(${d.room_id})">
                        🛋️ Open in Room Studio &rarr;
                    </button>
                `;
                gallery.appendChild(card);
            });
        } else {
            section.style.display = "none";
        }
    } catch (e) {
        console.error("Failed to load house designs:", e);
    }
}

// Whole House Unified Generation
async function generateWholeHouseDesign() {
    if (!currentHouseId) return;
    const btn = document.getElementById("btn-gen-whole-house");
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "✨ Generating Whole-House Visualizations (Multi-Room AI)...";
    btn.style.opacity = "0.7";

    try {
        const res = await fetch(`/api/house/${currentHouseId}/generate`, { method: "POST" });
        const data = await res.json();

        if (data.status === "success") {
            await loadActiveHouseDetails();
            const section = document.getElementById("whole-house-designs-section");
            if (section) {
                section.style.display = "block";
                section.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        } else {
            alert("Generation notice: " + (data.error || "Completed"));
        }
    } catch (e) {
        console.error("Whole-house generation error:", e);
        alert("Failed to generate whole-house designs.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        btn.style.opacity = "1";
    }
}

// ==============================================================================
// ROOM STUDIO (LEVEL 1)
// ==============================================================================

function openRoomStudio(roomId) {
    currentRoomId = roomId;
    switchStudioTab('room-studio');
    const select = document.getElementById("room-studio-select");
    if (select) select.value = roomId;
    loadActiveRoomStudio();
}

function onStudioRoomSelect() {
    const select = document.getElementById("room-studio-select");
    currentRoomId = parseInt(select.value, 10);
    loadActiveRoomStudio();
}

async function loadActiveRoomStudio() {
    if (!currentRoomId) return;

    try {
        const res = await fetch(`/api/room/${currentRoomId}`);
        const data = await res.json();
        currentRoomData = data.room;

        // Update badge
        const badge = document.getElementById("room-dimensions-badge");
        badge.innerText = `${currentRoomData.dimensions.length_ft} x ${currentRoomData.dimensions.width_ft} ft (${currentRoomData.dimensions.area_sqft} sq.ft)`;

        // Uploaded photos
        const imgGallery = document.getElementById("uploaded-room-images");
        imgGallery.innerHTML = "";
        (currentRoomData.images || []).forEach(img => {
            const thumb = document.createElement("img");
            thumb.src = img.image_path.startsWith("uploads") ? `/${img.image_path}` : img.image_path;
            thumb.style.cssText = "width:60px; height:60px; object-fit:cover; border-radius:8px; border:1px solid rgba(255,255,255,0.2);";
            imgGallery.appendChild(thumb);
        });

        // Computer Vision Analysis
        const cvCard = document.getElementById("cv-analysis-card");
        const cvContent = document.getElementById("cv-analysis-content");
        if (currentRoomData.analysis) {
            cvCard.style.display = "block";
            const ana = currentRoomData.analysis;
            const colors = (ana.dominant_colors || []).map(c => `<span class="swatch-pill">${c}</span>`).join(" ");
            const objects = (ana.detected_objects || []).map(o => `<span class="swatch-pill" style="background:rgba(99,102,241,0.15); color:#a5b4fc;">${o}</span>`).join(" ");

            cvContent.innerHTML = `
                <div style="margin-bottom:6px;"><strong>Detected Type:</strong> ${ana.room_type} (${ana.estimated_size} size)</div>
                <div style="margin-bottom:6px;"><strong>Detected Style:</strong> ${ana.detected_style}</div>
                <div style="margin-bottom:6px;"><strong>Floor Material:</strong> ${ana.floor_material}</div>
                <div style="margin-bottom:8px;"><strong>Dominant Colors:</strong> <div class="swatch-group">${colors}</div></div>
                <div><strong>Detected Furniture & Objects:</strong> <div class="swatch-group">${objects}</div></div>
            `;
        } else {
            cvCard.style.display = "none";
        }

        // Active Design & Visualization
        const prevContainer = document.getElementById("room-design-preview-container");
        const explText = document.getElementById("room-design-explanation");
        const recsCard = document.getElementById("room-recs-card");
        const recsContent = document.getElementById("room-recs-content");

        if (currentRoomData.designs && currentRoomData.designs.length > 0) {
            const latest = currentRoomData.designs[currentRoomData.designs.length - 1];
            currentDesignId = latest.id;
            prevContainer.innerHTML = `
                <img src="${latest.image_url}" style="width:100%; border-radius:14px; max-height:360px; object-fit:cover;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:10px; gap:8px; flex-wrap:wrap;">
                    <div style="display:flex; gap:8px;">
                        <button class="btn-secondary" style="font-size:12px; padding:6px 12px;" onclick="downloadDesignImage('${latest.image_url}')">
                            <i class="fas fa-download"></i> Save / Download
                        </button>
                        <button class="btn-secondary" style="font-size:12px; padding:6px 12px;" onclick="shareDesignLink(${latest.id}, '${latest.image_url}')">
                            <i class="fas fa-share-nodes"></i> Share
                        </button>
                    </div>
                    <button class="btn-secondary" style="font-size:12px; padding:6px 12px; border-color:rgba(251,191,36,0.4); color:#fbbf24;" onclick="openFeedbackDialog(${latest.id})">
                        <i class="fas fa-star"></i> Rate & Review
                    </button>
                </div>
            `;
            explText.style.display = "block";
            explText.innerHTML = `<strong>Architectural Rationale:</strong> ${latest.explanation || 'Custom design tailored to room layout and house styling.'}`;

            // Load recommendations & cost
            loadDesignDetails(latest.id);
        } else {
            prevContainer.innerHTML = `<p style="font-size:13px; color:#64748b; padding:40px;">No design generated yet. Click generate to visualize.</p>`;
            explText.style.display = "none";
            recsCard.style.display = "none";
        }
    } catch (e) {
        console.error("Failed to load room studio:", e);
    }
}

function downloadDesignImage(url) {
    const a = document.createElement("a");
    a.href = url;
    a.download = `decoraai_design_${Date.now()}.jpg`;
    a.target = "_blank";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

function shareDesignLink(designId, url) {
    const shareUrl = url.startsWith("http") ? url : (window.location.origin + url);
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl);
        alert("✓ Design link copied to clipboard: " + shareUrl);
    } else {
        prompt("Copy this design URL:", shareUrl);
    }
}

let activeFeedbackDesignId = null;

function openFeedbackDialog(designId) {
    activeFeedbackDesignId = designId || currentDesignId;
    document.getElementById("feedback-dialog").classList.add("active");
}

function closeFeedbackDialog() {
    document.getElementById("feedback-dialog").classList.remove("active");
}

async function submitDesignFeedback() {
    if (!activeFeedbackDesignId) return;
    const rating = parseInt(document.getElementById("feedback-rating").value) || 5;
    const feedback_text = document.getElementById("feedback-text").value.trim();

    try {
        const res = await fetch(`/api/design/${activeFeedbackDesignId}/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rating, feedback_text })
        });
        const data = await res.json();
        if (data.status === "success") {
            alert("✓ Thank you! Your feedback & rating have been saved.");
            closeFeedbackDialog();
            document.getElementById("feedback-text").value = "";
        }
    } catch (e) {
        console.error("Failed to submit feedback:", e);
    }
}

async function handleRoomImageUpload(input) {
    if (!currentRoomId || !input.files || input.files.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < input.files.length; i++) {
        formData.append("images", input.files[i]);
    }

    try {
        const res = await fetch(`/api/room/${currentRoomId}/upload`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (data.status === "success") {
            alert(`Uploaded ${data.uploaded_images.length} room photo(s).`);
            loadActiveRoomStudio();
        }
    } catch (e) {
        console.error("Upload failed:", e);
        alert("Failed to upload images.");
    }
}

async function runRoomVisionAnalysis() {
    if (!currentRoomId) return;

    try {
        const res = await fetch(`/api/room/${currentRoomId}/analyze`, { method: "POST" });
        const data = await res.json();
        if (data.status === "success") {
            loadActiveRoomStudio();
        }
    } catch (e) {
        console.error("Vision analysis failed:", e);
    }
}

function onRoomPaletteSelectChange(val) {
    const customInput = document.getElementById("room-custom-palette-input");
    if (val === "custom") {
        customInput.style.display = "block";
        customInput.focus();
    } else {
        customInput.style.display = "none";
    }
}

async function generateCurrentRoomDesign() {
    if (!currentRoomId) return;

    const btn = document.getElementById("btn-generate-room");
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = "✨ Generating Room Visualization...";
    btn.style.opacity = "0.7";

    const style = document.getElementById("room-style-override").value;
    const paletteSelect = document.getElementById("room-palette-override").value;
    const customPaletteInput = document.getElementById("room-custom-palette-input").value.trim();

    let palette = null;
    if (paletteSelect === "custom" && customPaletteInput) {
        palette = customPaletteInput;
    } else if (paletteSelect && paletteSelect !== "custom") {
        palette = paletteSelect;
    }

    try {
        const payload = { style };
        if (palette) payload.palette = palette;

        const res = await fetch(`/api/room/${currentRoomId}/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (data.status === "success") {
            loadActiveRoomStudio();
        } else {
            alert("Error: " + (data.error || "Could not generate design"));
        }
    } catch (e) {
        console.error("Room generation failed:", e);
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        btn.style.opacity = "1";
    }
}

async function loadDesignDetails(designId) {
    try {
        const res = await fetch(`/api/design/${designId}`);
        const data = await res.json();
        const recsCard = document.getElementById("room-recs-card");
        const recsContent = document.getElementById("room-recs-content");

        if (data.furniture_recommendations || data.materials) {
            recsCard.style.display = "block";

            let furnitureRows = "";
            (data.furniture_recommendations || []).forEach(f => {
                furnitureRows += `
                    <tr>
                        <td><strong>${f.name}</strong><br><span style="font-size:11px; color:#94a3b8;">${f.reason || ''}</span></td>
                        <td>${f.category}</td>
                        <td>${f.dimensions}</td>
                        <td style="color:#34d399; font-weight:600;">₹${f.estimated_cost.toLocaleString('en-IN')}</td>
                    </tr>
                `;
            });

            recsContent.innerHTML = `
                <h5 style="font-size:13px; color:#e2e8f0; margin-bottom:8px;">🛋️ Itemized Furniture Recommendations</h5>
                <table class="modern-table">
                    <thead>
                        <tr><th>Item</th><th>Category</th><th>Dimensions</th><th>Est. Cost</th></tr>
                    </thead>
                    <tbody>${furnitureRows}</tbody>
                </table>
            `;
        }

        // Load chats
        const chatBox = document.getElementById("room-chat-messages");
        if (data.chats && data.chats.length > 0) {
            chatBox.innerHTML = "";
            data.chats.forEach(c => {
                const bubble = document.createElement("div");
                bubble.className = `chat-bubble ${c.role}`;
                bubble.innerText = c.message;
                chatBox.appendChild(bubble);
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    } catch (e) {
        console.error("Failed to load design details:", e);
    }
}

async function sendRoomChatMessage() {
    const input = document.getElementById("room-chat-input");
    const msg = input.value.trim();
    if (!msg || !currentDesignId) {
        if (!currentDesignId) alert("Please generate a design first before chatting with AI.");
        return;
    }

    const chatBox = document.getElementById("room-chat-messages");

    // Add user bubble
    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble user";
    userBubble.innerText = msg;
    chatBox.appendChild(userBubble);
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Temporary thinking bubble
    const thinkingBubble = document.createElement("div");
    thinkingBubble.className = "chat-bubble assistant";
    thinkingBubble.innerText = "Thinking...";
    chatBox.appendChild(thinkingBubble);

    try {
        const res = await fetch(`/api/design/${currentDesignId}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        if (data.status === "success") {
            thinkingBubble.innerText = data.reply;
        } else {
            thinkingBubble.innerText = "Sorry, I encountered an issue processing your request.";
        }
    } catch (e) {
        thinkingBubble.innerText = "Network error communicating with AI designer.";
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ==============================================================================
// HOUSE COST & BUDGET (TAB 3)
// ==============================================================================

async function loadHouseCostTab() {
    if (!currentHouseId) return;

    try {
        const res = await fetch(`/api/house/${currentHouseId}/cost`);
        const data = await res.json();
        const est = data.estimated_cost || {};

        document.getElementById("house-cost-summary").innerHTML = `
            <div style="font-size:24px; font-weight:700; color:#34d399; margin-bottom:12px;">
                ₹${(est.total_cost || 0).toLocaleString('en-IN')}
            </div>
            <div><strong>Furniture Total:</strong> ₹${(est.furniture_cost || 0).toLocaleString('en-IN')}</div>
            <div><strong>Materials & Flooring:</strong> ₹${(est.materials_cost || 0).toLocaleString('en-IN')}</div>
            <div><strong>Lighting Fixtures:</strong> ₹${(est.lighting_cost || 0).toLocaleString('en-IN')}</div>
            <div><strong>Paint & Wall Finishes:</strong> ₹${(est.paint_cost || 0).toLocaleString('en-IN')}</div>
            <div><strong>Decor & Styling:</strong> ₹${(est.decor_cost || 0).toLocaleString('en-IN')}</div>
        `;

        const budget = data.total_budget || 1500000;
        const total = est.total_cost || 0;
        const diff = budget - total;

        document.getElementById("budget-comparison-box").innerHTML = `
            <div style="margin-bottom:8px;"><strong>Allocated House Budget:</strong> ₹${budget.toLocaleString('en-IN')}</div>
            <div style="margin-bottom:8px;"><strong>Estimated Project Cost:</strong> ₹${total.toLocaleString('en-IN')}</div>
            <div style="font-weight:600; color:${diff >= 0 ? '#34d399' : '#f87171'};">
                ${diff >= 0 ? `✅ Within Budget (₹${diff.toLocaleString('en-IN')} remaining)` : `⚠️ Budget Exceeded by ₹${Math.abs(diff).toLocaleString('en-IN')}`}
            </div>
        `;

        // Table
        let rows = "";
        (est.rooms || []).forEach(r => {
            const c = r.cost;
            rows += `
                <tr>
                    <td><strong>${r.room_name}</strong></td>
                    <td>₹${c.furniture_cost.toLocaleString('en-IN')}</td>
                    <td>₹${c.materials_cost.toLocaleString('en-IN')}</td>
                    <td>₹${c.lighting_cost.toLocaleString('en-IN')}</td>
                    <td>₹${c.paint_cost.toLocaleString('en-IN')}</td>
                    <td style="color:#34d399; font-weight:700;">₹${c.total_cost.toLocaleString('en-IN')}</td>
                </tr>
            `;
        });

        document.getElementById("room-cost-table-container").innerHTML = `
            <table class="modern-table">
                <thead>
                    <tr><th>Room</th><th>Furniture</th><th>Materials</th><th>Lighting</th><th>Paint</th><th>Room Total</th></tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    } catch (e) {
        console.error("Failed to load cost tab:", e);
    }
}

// ==============================================================================
// DIALOGS & FORMS
// ==============================================================================

function openCreateHouseDialog() {
    document.getElementById("create-house-dialog").classList.add("active");
}

function closeCreateHouseDialog() {
    document.getElementById("create-house-dialog").classList.remove("active");
}

function onPropertyTypeChange(val) {
    const villaGroup = document.getElementById("num-villas-group");
    if (val === "multi_villa" || val === "villa") {
        villaGroup.style.display = "block";
    } else {
        villaGroup.style.display = "none";
        document.getElementById("new-house-num-villas").value = "1";
    }
}

function onRoomConfigChange(val) {
    const customGroup = document.getElementById("custom-room-count-group");
    if (val === "custom") {
        customGroup.style.display = "block";
    } else {
        customGroup.style.display = "none";
    }
}

async function submitCreateHouse() {
    const name = document.getElementById("new-house-name").value.trim();
    const budget = parseFloat(document.getElementById("new-house-budget").value);
    const area = parseFloat(document.getElementById("new-house-area").value);
    const style = document.getElementById("new-house-style").value;
    const property_type = document.getElementById("new-house-property-type").value;
    const num_villas = parseInt(document.getElementById("new-house-num-villas").value) || 1;
    const room_config = document.getElementById("new-house-room-config").value;
    const custom_rooms = parseInt(document.getElementById("new-house-custom-rooms").value) || 6;
    const floors = parseInt(document.getElementById("new-house-floors").value) || 1;

    try {
        const res = await fetch("/api/house/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                total_budget: budget,
                approx_area_sqft: area,
                primary_style: style,
                property_type,
                num_villas,
                room_config,
                num_rooms: custom_rooms,
                floors
            })
        });
        const data = await res.json();
        if (data.status === "success") {
            closeCreateHouseDialog();
            currentHouseId = data.house.id;
            loadHouseProjects();
        }
    } catch (e) {
        console.error("Failed to create house:", e);
    }
}

function openAddRoomDialog() {
    document.getElementById("add-room-dialog").classList.add("active");
}

function closeAddRoomDialog() {
    document.getElementById("add-room-dialog").classList.remove("active");
}

async function submitAddRoom() {
    if (!currentHouseId) return;
    const name = document.getElementById("new-room-name").value.trim();
    const room_type = document.getElementById("new-room-type").value;
    const length = parseFloat(document.getElementById("new-room-length").value);
    const width = parseFloat(document.getElementById("new-room-width").value);

    try {
        const res = await fetch(`/api/house/${currentHouseId}/rooms`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                room_type,
                length_ft: length,
                width_ft: width
            })
        });
        const data = await res.json();
        if (data.status === "success") {
            closeAddRoomDialog();
            loadActiveHouseDetails();
        }
    } catch (e) {
        console.error("Failed to add room:", e);
    }
}

// ==============================================================================
// PALETTE & STYLE CUSTOMIZATION HANDLERS
// ==============================================================================

function openEditPaletteDialog() {
    if (!currentHouseData || !currentHouseData.style_profile) return;
    const profile = currentHouseData.style_profile;

    document.getElementById("edit-house-style").value = profile.primary_style || "Modern Luxury";
    
    let paletteText = "";
    if (Array.isArray(profile.main_palette)) {
        paletteText = profile.main_palette.join(", ");
    } else {
        paletteText = profile.main_palette || "Warm White, Beige, Walnut Wood";
    }
    document.getElementById("edit-house-palette").value = paletteText;
    document.getElementById("edit-house-flooring").value = profile.flooring_spec || "Light Italian Marble";
    document.getElementById("edit-house-lighting").value = profile.lighting_temp || "Warm White (3000K)";

    document.getElementById("edit-palette-dialog").classList.add("active");
}

function closeEditPaletteDialog() {
    document.getElementById("edit-palette-dialog").classList.remove("active");
}

function applyPresetPalette(colorsArray) {
    document.getElementById("edit-house-palette").value = colorsArray.join(", ");
}

async function submitEditHousePalette() {
    if (!currentHouseId) return;

    const style = document.getElementById("edit-house-style").value;
    const paletteStr = document.getElementById("edit-house-palette").value.trim();
    const flooring = document.getElementById("edit-house-flooring").value;
    const lighting = document.getElementById("edit-house-lighting").value;

    const paletteList = paletteStr.split(",").map(c => c.trim()).filter(c => c.length > 0);

    try {
        const res = await fetch(`/api/house/${currentHouseId}/profile`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                primary_style: style,
                main_palette: paletteList,
                flooring_spec: flooring,
                lighting_temp: lighting
            })
        });

        const data = await res.json();
        if (data.status === "success") {
            closeEditPaletteDialog();
            loadActiveHouseDetails();
        } else {
            alert("Error: " + (data.error || "Could not update palette"));
        }
    } catch (e) {
        console.error("Failed to update style profile:", e);
    }
}

// Global modal viewer for gallery
const galleryImages = document.querySelectorAll(".gallery-card img");
const modal = document.createElement("div");
modal.classList.add("image-modal");
modal.innerHTML = `<img id="modal-image" alt="Enlarged view">`;
document.body.appendChild(modal);

galleryImages.forEach(image => {
    image.addEventListener("click", () => {
        modal.classList.add("active");
        document.getElementById("modal-image").src = image.src;
    });
});

modal.addEventListener("click", () => {
    modal.classList.remove("active");
});

// ==============================================================================
// AUTHENTICATION STATE HANDLER
// ==============================================================================
async function checkAuthStatus() {
    try {
        const res = await fetch("/api/auth/me");
        const data = await res.json();
        const loginLink = document.getElementById("nav-login-link");
        const userProfile = document.getElementById("nav-user-profile");
        const userNameSpan = document.getElementById("nav-user-name");
        const adminDbLink = document.getElementById("nav-admin-db-link");

        if (data.authenticated && data.user) {
            if (loginLink) loginLink.style.display = "none";
            if (userProfile) {
                userProfile.style.display = "flex";
                userNameSpan.innerText = `👋 ${data.user.name.split(' ')[0]}`;
            }
            if (adminDbLink) {
                adminDbLink.style.display = data.user.is_admin ? "inline-flex" : "none";
            }
        } else {
            if (loginLink) loginLink.style.display = "inline-block";
            if (userProfile) userProfile.style.display = "none";
            if (adminDbLink) adminDbLink.style.display = "none";
        }
    } catch (e) {
        console.error("Auth check failed:", e);
    }
}

async function handleLogout() {
    try {
        await fetch("/api/auth/logout", { method: "POST" });
        window.location.reload();
    } catch (e) {
        console.error("Logout failed:", e);
    }
}

// Check auth on load
document.addEventListener("DOMContentLoaded", () => {
    checkAuthStatus();
});