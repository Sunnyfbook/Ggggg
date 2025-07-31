 // Enhanced HilltopAds Container Management
class HilltopAdsManager {
    constructor() {
        this.adSlots = [
            'ad-top', 'ad-middle', 'ad-bottom', 'ad-preroll', 
            'ad-post-reactions', 'ad-footer', 'ad-sidebar',
            'ad-video-preroll', 'ad-video-overlay', 'ad-video-postroll'
        ];
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupAds());
        } else {
            this.setupAds();
        }
    }

    setupAds() {
        // Load ads in designated containers
        this.loadAdsInContainers();
        
        // Monitor for rogue ads and relocate them
        this.monitorAndRelocateAds();
        
        // Set up mutation observer to catch dynamically injected ads
        this.setupMutationObserver();
    }

    loadAdsInContainers() {
        // Example: Load specific HilltopAds in designated containers
        const adConfigs = {
            'ad-top': '728x90',
            'ad-middle': '728x90', 
            'ad-bottom': '728x90',
            'ad-sidebar': '300x250',
            'ad-post-reactions': '320x50',
            'ad-footer': '728x90'
        };

        Object.entries(adConfigs).forEach(([containerId, size]) => {
            this.loadAdInContainer(containerId, size);
        });
    }

    loadAdInContainer(containerId, size) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Clear existing content
        container.innerHTML = '';
        
        // Add loading state
        container.classList.add('loading');
        
        try {
            // Create ad wrapper div
            const adWrapper = document.createElement('div');
            adWrapper.className = 'ad-wrapper';
            adWrapper.setAttribute('data-ad-size', size);
            
            // Insert HilltopAds script/code here
            // Replace 'YOUR_AD_ZONE_ID' with actual zone IDs
            const adScript = document.createElement('script');
            adScript.type = 'text/javascript';
            adScript.innerHTML = `
                (function() {
                    var adContainer = document.querySelector('#${containerId} .ad-wrapper');
                    if (adContainer && typeof hilltopads !== 'undefined') {
                        // Your HilltopAds initialization code here
                        // Example: hilltopads.show('YOUR_ZONE_ID', adContainer);
                        console.log('Loading ad in container: ${containerId}');
                    }
                })();
            `;
            
            adWrapper.appendChild(adScript);
            container.appendChild(adWrapper);
            
            // Remove loading state after a delay
            setTimeout(() => {
                container.classList.remove('loading');
            }, 2000);
            
        } catch (error) {
            console.error(`Error loading ad in ${containerId}:`, error);
            container.classList.remove('loading');
            container.classList.add('error');
        }
    }

    monitorAndRelocateAds() {
        // Check every 2 seconds for misplaced ads
        const checkInterval = setInterval(() => {
            this.relocateMisplacedAds();
        }, 2000);

        // Stop checking after 30 seconds
        setTimeout(() => {
            clearInterval(checkInterval);
        }, 30000);
    }

    relocateMisplacedAds() {
        // Find ads that appear at the bottom of the body
        const bodyChildren = Array.from(document.body.children);
        
        bodyChildren.forEach(element => {
            if (this.isLikelyAd(element) && !this.isInDesignatedContainer(element)) {
                this.relocateAd(element);
            }
        });

        // Also check for fixed position elements
        const fixedElements = document.querySelectorAll('[style*="position: fixed"], [style*="position:fixed"]');
        fixedElements.forEach(element => {
            if (this.isLikelyAd(element)) {
                this.relocateAd(element);
            }
        });
    }

    isLikelyAd(element) {
        // Check if element is likely an ad
        const adIndicators = [
            'hilltop', 'ads', 'banner', 'advertisement',
            'ad-container', 'ad-unit', 'ad-slot'
        ];
        
        const elementHTML = element.outerHTML.toLowerCase();
        const hasAdIndicator = adIndicators.some(indicator => 
            elementHTML.includes(indicator)
        );
        
        // Check for iframe ads
        const hasAdIframe = element.querySelector('iframe[src*="ads"], iframe[src*="ad"]');
        
        // Check for script tags with ad-related content
        const hasAdScript = element.querySelector('script') && 
            elementHTML.includes('ad') || elementHTML.includes('banner');
            
        return hasAdIndicator || hasAdIframe || hasAdScript;
    }

    isInDesignatedContainer(element) {
        // Check if element is already in one of our ad containers
        const adContainers = this.adSlots.map(id => document.getElementById(id));
        
        return adContainers.some(container => {
            return container && (container.contains(element) || element.contains(container));
        });
    }

    relocateAd(element) {
        // Find the best container for this ad
        const targetContainer = this.findBestContainer(element);
        
        if (targetContainer && !targetContainer.hasChildNodes()) {
            // Remove original element from its current position
            const originalParent = element.parentNode;
            if (originalParent) {
                originalParent.removeChild(element);
            }
            
            // Create wrapper and move ad
            const wrapper = document.createElement('div');
            wrapper.className = 'ad-wrapper relocated';
            wrapper.appendChild(element);
            
            // Add to target container
            targetContainer.appendChild(wrapper);
            targetContainer.classList.remove('loading');
            
            console.log('Relocated ad to container:', targetContainer.id);
        }
    }

    findBestContainer(element) {
        // Logic to find the best available container
        const availableContainers = this.adSlots
            .map(id => document.getElementById(id))
            .filter(container => container && !container.hasChildNodes());
            
        if (availableContainers.length === 0) return null;
        
        // Prioritize containers based on page position
        const priority = ['ad-top', 'ad-middle', 'ad-sidebar', 'ad-bottom', 'ad-footer'];
        
        for (const containerId of priority) {
            const container = availableContainers.find(c => c.id === containerId);
            if (container) return container;
        }
        
        return availableContainers[0];
    }

    setupMutationObserver() {
        // Watch for dynamically added elements
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE && this.isLikelyAd(node)) {
                        // Delay to allow ad to fully load
                        setTimeout(() => {
                            if (!this.isInDesignatedContainer(node)) {
                                this.relocateAd(node);
                            }
                        }, 1000);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Stop observing after 60 seconds
        setTimeout(() => {
            observer.disconnect();
        }, 60000);
    }

    // Method to manually trigger ad relocation
    relocateAllAds() {
        this.relocateMisplacedAds();
    }

    // Method to refresh ads in containers
    refreshAds() {
        this.adSlots.forEach(slotId => {
            const container = document.getElementById(slotId);
            if (container) {
                container.innerHTML = '';
                container.classList.add('loading');
                // Reload ad logic here
                setTimeout(() => {
                    container.classList.remove('loading');
                }, 2000);
            }
        });
    }
}

// Additional CSS injection to prevent bottom ads
function injectAdPreventionCSS() {
    const style = document.createElement('style');
    style.textContent = `
        /* Prevent ads from appearing at bottom */
        body > div:not(.container):not(.ad-slot):not([class]):last-child {
            display: none !important;
        }
        
        /* Hide fixed position ads that aren't in containers */
        body > div[style*="position: fixed"]:not([id]):not([class]),
        body > div[style*="position:fixed"]:not([id]):not([class]),
        body > iframe[style*="position: fixed"]:not([id]):not([class]),
        body > iframe[style*="position:fixed"]:not([id]):not([class]) {
            display: none !important;
        }
        
        /* Force ads to stay within containers */
        .ad-slot {
            position: relative !important;
            overflow: hidden !important;
            z-index: 1 !important;
        }
        
        .ad-slot .ad-wrapper {
            width: 100% !important;
            height: 100% !important;
            position: relative !important;
        }
        
        /* Prevent z-index stacking issues */
        .ad-slot * {
            position: relative !important;
            z-index: auto !important;
        }
        
        /* Hide elements that try to break out */
        .ad-slot iframe {
            max-width: 100% !important;
            max-height: 300px !important;
        }
    `;
    document.head.appendChild(style);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Inject prevention CSS first
    injectAdPreventionCSS();
    
    // Initialize ad manager
    const adManager = new HilltopAdsManager();
    
    // Make it globally available for debugging
    window.adManager = adManager;
    
    // Additional check after page fully loads
    window.addEventListener('load', () => {
        setTimeout(() => {
            adManager.relocateAllAds();
        }, 3000);
    });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HilltopAdsManager;
}
