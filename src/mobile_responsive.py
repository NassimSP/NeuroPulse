"""
Mobile-Responsive Optimization for NeuroPulse Enterprise
Provides adaptive layouts, touch-friendly interfaces, and mobile-specific features
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class MobileOptimizationManager:
    def __init__(self):
        self.device_analytics_file = 'device_analytics_data.json'
        self.mobile_sessions_file = 'mobile_sessions_data.json'
        self.responsive_config_file = 'responsive_config_data.json'
        
        self.load_data()
    
    def load_data(self):
        """Load mobile optimization data"""
        self.device_analytics = self._load_json_file(self.device_analytics_file, {})
        self.mobile_sessions = self._load_json_file(self.mobile_sessions_file, {})
        self.responsive_config = self._load_json_file(self.responsive_config_file, self._get_default_config())
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        """Load JSON file with fallback to default"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_default_config(self) -> dict:
        """Get default responsive configuration"""
        return {
            'breakpoints': {
                'mobile': 768,
                'tablet': 1024,
                'desktop': 1200,
                'large_desktop': 1440
            },
            'mobile_features': {
                'touch_optimized': True,
                'swipe_navigation': True,
                'progressive_loading': True,
                'offline_capability': True,
                'push_notifications': True
            },
            'adaptive_ui': {
                'font_scaling': True,
                'button_sizing': True,
                'navigation_collapse': True,
                'content_prioritization': True
            },
            'performance_optimization': {
                'image_compression': True,
                'lazy_loading': True,
                'service_worker': True,
                'caching_strategy': 'cache_first'
            }
        }
    
    def track_device_usage(self, user_id: str, device_info: dict, session_data: dict):
        """Track device usage patterns for optimization"""
        session_id = f"{user_id}_{datetime.now().isoformat()}"
        
        device_session = {
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'device_info': {
                'device_type': device_info.get('device_type', 'unknown'),
                'screen_width': device_info.get('screen_width'),
                'screen_height': device_info.get('screen_height'),
                'user_agent': device_info.get('user_agent', ''),
                'touch_capable': device_info.get('touch_capable', False),
                'network_type': device_info.get('network_type', 'unknown')
            },
            'session_metrics': {
                'duration_minutes': session_data.get('duration_minutes', 0),
                'pages_visited': session_data.get('pages_visited', 0),
                'interactions': session_data.get('interactions', 0),
                'errors_encountered': session_data.get('errors_encountered', 0),
                'loading_performance': session_data.get('loading_performance', {}),
                'user_satisfaction': session_data.get('user_satisfaction')
            },
            'feature_usage': {
                'touch_gestures_used': session_data.get('touch_gestures_used', 0),
                'voice_input_used': session_data.get('voice_input_used', False),
                'offline_mode_used': session_data.get('offline_mode_used', False),
                'notifications_interacted': session_data.get('notifications_interacted', 0)
            }
        }
        
        self.mobile_sessions[session_id] = device_session
        self._save_json_file(self.mobile_sessions_file, self.mobile_sessions)
        
        # Update device analytics
        self._update_device_analytics(device_info, session_data)
    
    def _update_device_analytics(self, device_info: dict, session_data: dict):
        """Update aggregate device analytics"""
        device_type = device_info.get('device_type', 'unknown')
        
        if device_type not in self.device_analytics:
            self.device_analytics[device_type] = {
                'total_sessions': 0,
                'total_users': set(),
                'average_session_duration': 0,
                'common_screen_sizes': {},
                'performance_metrics': {
                    'average_load_time': 0,
                    'error_rate': 0,
                    'satisfaction_score': 0
                },
                'feature_adoption': {
                    'touch_gestures': 0,
                    'voice_input': 0,
                    'offline_mode': 0
                }
            }
        
        device_stats = self.device_analytics[device_type]
        device_stats['total_sessions'] += 1
        
        # Track screen sizes
        screen_key = f"{device_info.get('screen_width', 0)}x{device_info.get('screen_height', 0)}"
        device_stats['common_screen_sizes'][screen_key] = device_stats['common_screen_sizes'].get(screen_key, 0) + 1
        
        # Update performance metrics
        load_time = session_data.get('loading_performance', {}).get('page_load_time', 0)
        if load_time > 0:
            current_avg = device_stats['performance_metrics']['average_load_time']
            sessions = device_stats['total_sessions']
            device_stats['performance_metrics']['average_load_time'] = (current_avg * (sessions - 1) + load_time) / sessions
        
        # Convert set to list for JSON serialization
        device_stats['total_users'] = list(device_stats['total_users'])
        
        self._save_json_file(self.device_analytics_file, self.device_analytics)
    
    def get_responsive_css(self, device_type: str = None) -> str:
        """Generate responsive CSS based on device analytics"""
        css_rules = []
        
        # Base responsive styles
        css_rules.append("""
/* Mobile-First Responsive Design */
* {
    box-sizing: border-box;
}

/* Base mobile styles */
body {
    font-size: 16px;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Touch-friendly buttons */
.btn {
    min-height: 44px;
    min-width: 44px;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    touch-action: manipulation;
    user-select: none;
}

/* Responsive navigation */
.navbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    padding: 1rem;
}

.nav-toggle {
    display: none;
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
}

.nav-menu {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    width: 100%;
}

.nav-item {
    margin: 0 0.5rem;
}

/* Form optimizations */
.form-group {
    margin-bottom: 1.5rem;
}

.form-control {
    width: 100%;
    padding: 0.75rem;
    font-size: 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    transition: border-color 0.3s ease;
}

.form-control:focus {
    outline: none;
    border-color: hsl(var(--primary-color));
}

/* Card layouts */
.card-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}

.card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

/* Loading states */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid hsl(var(--primary-color));
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Utility classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }
.d-none { display: none; }
.d-block { display: block; }
.d-flex { display: flex; }
.d-grid { display: grid; }

/* Spacing utilities */
.m-0 { margin: 0; }
.m-1 { margin: 0.25rem; }
.m-2 { margin: 0.5rem; }
.m-3 { margin: 1rem; }
.m-4 { margin: 1.5rem; }
.m-5 { margin: 3rem; }

.p-0 { padding: 0; }
.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 1rem; }
.p-4 { padding: 1.5rem; }
.p-5 { padding: 3rem; }

/* Tablet styles */
@media (min-width: 768px) {
    .container {
        padding: 0 2rem;
    }
    
    .card-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .nav-menu {
        width: auto;
    }
    
    .btn {
        padding: 0.875rem 2rem;
    }
}

/* Desktop styles */
@media (min-width: 1024px) {
    .card-grid {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .nav-toggle {
        display: none;
    }
    
    .container {
        padding: 0 2rem;
    }
}

/* Large desktop styles */
@media (min-width: 1200px) {
    .container {
        padding: 0 3rem;
    }
    
    .card-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}

/* Mobile-specific optimizations */
@media (max-width: 767px) {
    .nav-toggle {
        display: block;
    }
    
    .nav-menu {
        display: none;
        flex-direction: column;
        width: 100%;
        margin-top: 1rem;
    }
    
    .nav-menu.active {
        display: flex;
    }
    
    .nav-item {
        margin: 0.5rem 0;
    }
    
    .btn {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .table-responsive {
        overflow-x: auto;
    }
    
    .modal {
        margin: 1rem;
    }
    
    .social-quick-actions {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .social-quick-actions .btn {
        width: 100%;
    }
    
    .quick-navigation .row {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    
    .achievement-stat {
        flex-direction: column;
        text-align: center;
    }
    
    .chat-container {
        height: 60vh;
    }
    
    .message-input-container {
        position: sticky;
        bottom: 0;
        background: white;
        z-index: 10;
    }
}

/* Touch-specific optimizations */
@media (hover: none) and (pointer: coarse) {
    .card:hover {
        transform: none;
    }
    
    .btn:hover {
        transform: none;
    }
    
    .nav-card:hover {
        transform: none;
    }
    
    /* Increase touch targets */
    .btn, .form-control, .nav-link {
        min-height: 48px;
    }
    
    /* Remove hover effects on touch devices */
    .challenge-card:hover,
    .study-group-item:hover,
    .performer-item:hover {
        transform: none;
        box-shadow: var(--shadow-sm);
    }
}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
    .btn {
        border-width: 0.5px;
    }
    
    .card {
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    }
}

/* Landscape orientation on mobile */
@media (max-width: 767px) and (orientation: landscape) {
    .chat-container {
        height: 50vh;
    }
    
    .video-session-container {
        height: 70vh;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    :root {
        --surface: #1a1a1a;
        --surface-alt: #2d2d2d;
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
        --text-muted: #808080;
    }
    
    body {
        background-color: var(--surface);
        color: var(--text-primary);
    }
    
    .card {
        background: var(--surface-alt);
        color: var(--text-primary);
    }
    
    .form-control {
        background: var(--surface-alt);
        border-color: #404040;
        color: var(--text-primary);
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
    
    .loading {
        animation: none;
        border: 3px solid #f3f3f3;
        border-top-color: hsl(var(--primary-color));
    }
}

/* Print styles */
@media print {
    .navbar, .social-quick-actions, .quick-navigation {
        display: none;
    }
    
    .card {
        box-shadow: none;
        border: 1px solid #ddd;
    }
    
    body {
        font-size: 12pt;
        line-height: 1.4;
    }
}
""")
        
        return '\n'.join(css_rules)
    
    def get_mobile_javascript(self) -> str:
        """Generate mobile-specific JavaScript optimizations"""
        return """
// Mobile-Responsive JavaScript Enhancements
class MobileOptimization {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupTouchOptimizations();
        this.setupResponsiveNavigation();
        this.setupProgressiveLoading();
        this.setupOfflineSupport();
        this.trackDeviceMetrics();
    }
    
    setupTouchOptimizations() {
        // Enable touch gestures
        let startX, startY, endX, endY;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            this.handleSwipeGesture(startX, startY, endX, endY);
        }, { passive: true });
        
        // Prevent double-tap zoom on buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('touchend', (e) => {
                e.preventDefault();
                btn.click();
            });
        });
        
        // Improve scroll performance
        if ('scrollBehavior' in document.documentElement.style) {
            document.documentElement.style.scrollBehavior = 'smooth';
        }
    }
    
    handleSwipeGesture(startX, startY, endX, endY) {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const minSwipeDistance = 50;
        
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
            if (deltaX > 0) {
                this.onSwipeRight();
            } else {
                this.onSwipeLeft();
            }
        }
    }
    
    onSwipeRight() {
        // Navigate back or show sidebar
        const backButton = document.querySelector('[data-back-action]');
        if (backButton) {
            backButton.click();
        }
    }
    
    onSwipeLeft() {
        // Navigate forward or hide sidebar
        const forwardButton = document.querySelector('[data-forward-action]');
        if (forwardButton) {
            forwardButton.click();
        }
    }
    
    setupResponsiveNavigation() {
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
                navToggle.setAttribute('aria-expanded', 
                    navMenu.classList.contains('active'));
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                    navMenu.classList.remove('active');
                    navToggle.setAttribute('aria-expanded', 'false');
                }
            });
        }
    }
    
    setupProgressiveLoading() {
        // Lazy load images
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
        
        // Progressive content loading
        this.loadCriticalContent();
    }
    
    loadCriticalContent() {
        // Load above-the-fold content first
        const criticalSections = document.querySelectorAll('[data-critical]');
        criticalSections.forEach(section => {
            section.classList.add('loaded');
        });
        
        // Defer non-critical content
        setTimeout(() => {
            const deferredSections = document.querySelectorAll('[data-defer]');
            deferredSections.forEach(section => {
                section.classList.add('loaded');
            });
        }, 100);
    }
    
    setupOfflineSupport() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('Service Worker registered');
                })
                .catch(error => {
                    console.log('Service Worker registration failed');
                });
        }
        
        // Handle online/offline status
        window.addEventListener('online', () => {
            this.showConnectionStatus('online');
            this.syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            this.showConnectionStatus('offline');
        });
    }
    
    showConnectionStatus(status) {
        const statusIndicator = document.querySelector('.connection-status');
        if (statusIndicator) {
            statusIndicator.textContent = status === 'online' ? 'Connected' : 'Offline Mode';
            statusIndicator.className = `connection-status ${status}`;
        }
    }
    
    syncOfflineData() {
        // Sync any offline data when connection is restored
        const offlineData = this.getOfflineData();
        if (offlineData.length > 0) {
            this.uploadOfflineData(offlineData);
        }
    }
    
    getOfflineData() {
        try {
            const data = localStorage.getItem('offline_data');
            return data ? JSON.parse(data) : [];
        } catch (e) {
            return [];
        }
    }
    
    uploadOfflineData(data) {
        // Upload offline data to server
        fetch('/api/sync-offline-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).then(() => {
            localStorage.removeItem('offline_data');
        }).catch(error => {
            console.error('Failed to sync offline data:', error);
        });
    }
    
    trackDeviceMetrics() {
        const deviceInfo = {
            device_type: this.getDeviceType(),
            screen_width: window.screen.width,
            screen_height: window.screen.height,
            user_agent: navigator.userAgent,
            touch_capable: 'ontouchstart' in window,
            network_type: this.getNetworkType()
        };
        
        const sessionData = {
            duration_minutes: 0,
            pages_visited: 1,
            interactions: 0,
            loading_performance: {
                page_load_time: performance.now()
            }
        };
        
        // Track session start
        this.sessionStart = Date.now();
        this.interactionCount = 0;
        
        // Track interactions
        ['click', 'touch', 'keypress'].forEach(event => {
            document.addEventListener(event, () => {
                this.interactionCount++;
            });
        });
        
        // Send metrics on page unload
        window.addEventListener('beforeunload', () => {
            this.sendDeviceMetrics(deviceInfo, {
                ...sessionData,
                duration_minutes: (Date.now() - this.sessionStart) / 60000,
                interactions: this.interactionCount
            });
        });
    }
    
    getDeviceType() {
        if (/Mobi|Android/i.test(navigator.userAgent)) {
            return 'mobile';
        } else if (/Tablet|iPad/i.test(navigator.userAgent)) {
            return 'tablet';
        } else {
            return 'desktop';
        }
    }
    
    getNetworkType() {
        if ('connection' in navigator) {
            return navigator.connection.effectiveType || 'unknown';
        }
        return 'unknown';
    }
    
    sendDeviceMetrics(deviceInfo, sessionData) {
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/track-device-usage', JSON.stringify({
                device_info: deviceInfo,
                session_data: sessionData
            }));
        }
    }
    
    // Accessibility improvements
    setupAccessibility() {
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
        
        // ARIA live regions for dynamic content
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        document.body.appendChild(liveRegion);
        
        this.liveRegion = liveRegion;
    }
    
    announceToScreenReader(message) {
        if (this.liveRegion) {
            this.liveRegion.textContent = message;
            setTimeout(() => {
                this.liveRegion.textContent = '';
            }, 1000);
        }
    }
}

// Initialize mobile optimizations when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MobileOptimization();
});

// Service Worker for offline capability
const CACHE_NAME = 'neuropulse-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
    );
});
"""
    
    def get_device_analytics_report(self, institution_id: str = None) -> dict:
        """Generate device usage analytics report"""
        total_sessions = sum(stats['total_sessions'] for stats in self.device_analytics.values())
        
        if total_sessions == 0:
            return {'message': 'No device analytics data available'}
        
        # Device type distribution
        device_distribution = {}
        for device_type, stats in self.device_analytics.items():
            percentage = (stats['total_sessions'] / total_sessions) * 100
            device_distribution[device_type] = {
                'sessions': stats['total_sessions'],
                'percentage': round(percentage, 2),
                'avg_session_duration': stats.get('average_session_duration', 0),
                'performance_metrics': stats.get('performance_metrics', {})
            }
        
        # Screen size analysis
        popular_screen_sizes = self._analyze_screen_sizes()
        
        # Performance analysis
        performance_analysis = self._analyze_mobile_performance()
        
        return {
            'generated_at': datetime.now().isoformat(),
            'total_sessions': total_sessions,
            'device_distribution': device_distribution,
            'popular_screen_sizes': popular_screen_sizes,
            'performance_analysis': performance_analysis,
            'mobile_optimization_score': self._calculate_mobile_optimization_score(),
            'recommendations': self._generate_mobile_recommendations()
        }
    
    def _analyze_screen_sizes(self) -> dict:
        """Analyze popular screen sizes across devices"""
        all_screen_sizes = {}
        
        for device_type, stats in self.device_analytics.items():
            for screen_size, count in stats.get('common_screen_sizes', {}).items():
                all_screen_sizes[screen_size] = all_screen_sizes.get(screen_size, 0) + count
        
        # Sort by popularity
        sorted_sizes = sorted(all_screen_sizes.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'most_popular': sorted_sizes[:5],
            'total_unique_sizes': len(all_screen_sizes),
            'mobile_dominant': self._is_mobile_dominant(sorted_sizes)
        }
    
    def _is_mobile_dominant(self, screen_sizes: list) -> bool:
        """Check if mobile screen sizes dominate"""
        mobile_sessions = 0
        total_sessions = 0
        
        for size_key, count in screen_sizes:
            total_sessions += count
            width = int(size_key.split('x')[0]) if 'x' in size_key else 0
            if width <= 768:  # Mobile breakpoint
                mobile_sessions += count
        
        return (mobile_sessions / total_sessions) > 0.5 if total_sessions > 0 else False
    
    def _analyze_mobile_performance(self) -> dict:
        """Analyze mobile performance metrics"""
        mobile_stats = self.device_analytics.get('mobile', {})
        tablet_stats = self.device_analytics.get('tablet', {})
        desktop_stats = self.device_analytics.get('desktop', {})
        
        return {
            'mobile_load_time': mobile_stats.get('performance_metrics', {}).get('average_load_time', 0),
            'tablet_load_time': tablet_stats.get('performance_metrics', {}).get('average_load_time', 0),
            'desktop_load_time': desktop_stats.get('performance_metrics', {}).get('average_load_time', 0),
            'mobile_error_rate': mobile_stats.get('performance_metrics', {}).get('error_rate', 0),
            'performance_gap': self._calculate_performance_gap()
        }
    
    def _calculate_performance_gap(self) -> float:
        """Calculate performance gap between mobile and desktop"""
        mobile_load_time = self.device_analytics.get('mobile', {}).get('performance_metrics', {}).get('average_load_time', 0)
        desktop_load_time = self.device_analytics.get('desktop', {}).get('performance_metrics', {}).get('average_load_time', 0)
        
        if desktop_load_time > 0:
            gap = ((mobile_load_time - desktop_load_time) / desktop_load_time) * 100
            return round(gap, 2)
        
        return 0
    
    def _calculate_mobile_optimization_score(self) -> float:
        """Calculate overall mobile optimization score"""
        factors = []
        
        # Performance factor
        mobile_stats = self.device_analytics.get('mobile', {})
        load_time = mobile_stats.get('performance_metrics', {}).get('average_load_time', 0)
        performance_score = max(0, 100 - (load_time / 1000 * 20))  # Penalize slow load times
        factors.append(performance_score)
        
        # Error rate factor
        error_rate = mobile_stats.get('performance_metrics', {}).get('error_rate', 0)
        error_score = max(0, 100 - (error_rate * 100))
        factors.append(error_score)
        
        # Feature adoption factor
        feature_adoption = mobile_stats.get('feature_adoption', {})
        touch_usage = feature_adoption.get('touch_gestures', 0)
        adoption_score = min(100, touch_usage * 10)  # Score based on touch gesture usage
        factors.append(adoption_score)
        
        # Overall score
        return round(sum(factors) / len(factors), 2) if factors else 0
    
    def _generate_mobile_recommendations(self) -> list:
        """Generate mobile optimization recommendations"""
        recommendations = []
        
        mobile_stats = self.device_analytics.get('mobile', {})
        load_time = mobile_stats.get('performance_metrics', {}).get('average_load_time', 0)
        
        if load_time > 3000:  # 3 seconds
            recommendations.append({
                'priority': 'high',
                'category': 'performance',
                'suggestion': 'Optimize images and enable compression to reduce mobile load times',
                'impact': 'Improve user experience and reduce bounce rate'
            })
        
        if self.device_analytics.get('mobile', {}).get('total_sessions', 0) > 0:
            mobile_percentage = (mobile_stats.get('total_sessions', 0) / 
                               sum(stats['total_sessions'] for stats in self.device_analytics.values())) * 100
            
            if mobile_percentage > 60:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'design',
                    'suggestion': 'Consider mobile-first design approach given high mobile usage',
                    'impact': 'Better user experience for majority of users'
                })
        
        error_rate = mobile_stats.get('performance_metrics', {}).get('error_rate', 0)
        if error_rate > 0.05:  # 5% error rate
            recommendations.append({
                'priority': 'high',
                'category': 'stability',
                'suggestion': 'Investigate and fix mobile-specific errors',
                'impact': 'Reduce user frustration and improve retention'
            })
        
        return recommendations

# Initialize global mobile optimization manager
mobile_manager = MobileOptimizationManager()