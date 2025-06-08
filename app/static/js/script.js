/**
 * JavaScript principal para StreamFlix
 * Funcionalidades interactivas y mejoras de UX
 */

// ===== VARIABLES GLOBALES =====
let isLoading = false;

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Inicializar componentes
    initNavbar();
    initMovieCards();
    initVideoPlayer();
    initSearch();
    initLoadingStates();
    initScrollEffects();
    initTooltips();
    
    console.log('StreamFlix inicializado correctamente');
}

// ===== NAVEGACIÓN =====
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    
    // Efecto de scroll en navbar
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Cerrar dropdown al hacer click fuera
    document.addEventListener('click', function(event) {
        const dropdowns = document.querySelectorAll('.dropdown-menu.show');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(event.target) && !dropdown.previousElementSibling.contains(event.target)) {
                const bsDropdown = bootstrap.Dropdown.getInstance(dropdown.previousElementSibling);
                if (bsDropdown) {
                    bsDropdown.hide();
                }
            }
        });
    });
}

// ===== TARJETAS DE PELÍCULAS =====
function initMovieCards() {
    const movieCards = document.querySelectorAll('.movie-card');
    
    movieCards.forEach(card => {
        // Efecto hover mejorado
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.zIndex = '1';
        });
        
        // Lazy loading para imágenes
        const img = card.querySelector('.movie-poster');
        if (img && img.dataset.src) {
            observeImage(img);
        }
    });
}

// ===== LAZY LOADING DE IMÁGENES =====
function observeImage(img) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const image = entry.target;
                image.src = image.dataset.src;
                image.classList.remove('lazy');
                imageObserver.unobserve(image);
            }
        });
    });
    
    imageObserver.observe(img);
}

// ===== REPRODUCTOR DE VIDEO =====
function initVideoPlayer() {
    const videoContainers = document.querySelectorAll('.video-player');
    
    videoContainers.forEach(container => {
        const video = container.querySelector('video');
        const iframe = container.querySelector('iframe');
        
        if (video) {
            // Controles personalizados para video HTML5
            video.addEventListener('loadstart', function() {
                showLoading();
            });
            
            video.addEventListener('canplay', function() {
                hideLoading();
            });
            
            video.addEventListener('error', function() {
                hideLoading();
                showError('Error al cargar el video');
            });
        }
        
        if (iframe) {
            // Manejar carga de iframe
            iframe.addEventListener('load', function() {
                hideLoading();
            });
        }
    });
}

// ===== BÚSQUEDA =====
function initSearch() {
    const searchForm = document.querySelector('form[action*="search"]');
    const searchInput = document.querySelector('input[name="q"]');
    
    if (searchInput) {
        // Búsqueda en tiempo real (debounced)
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 2) {
                    performLiveSearch(this.value);
                }
            }, 500);
        });
        
        // Limpiar resultados cuando se borra la búsqueda
        searchInput.addEventListener('keyup', function() {
            if (this.value.length === 0) {
                clearSearchResults();
            }
        });
    }
}

function performLiveSearch(query) {
    // Implementar búsqueda AJAX aquí si es necesario
    console.log('Buscando:', query);
}

function clearSearchResults() {
    const resultsContainer = document.querySelector('#search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = '';
    }
}

// ===== ESTADOS DE CARGA =====
function initLoadingStates() {
    // Interceptar formularios para mostrar loading
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                showButtonLoading(submitBtn);
            }
        });
    });
    
    // Interceptar enlaces que requieren carga
    const loadingLinks = document.querySelectorAll('a[data-loading="true"]');
    loadingLinks.forEach(link => {
        link.addEventListener('click', function() {
            showLoading();
        });
    });
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
        isLoading = true;
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
        isLoading = false;
    }
}

function showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Cargando...';
    button.disabled = true;
    
    // Restaurar después de 5 segundos como fallback
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 5000);
}

// ===== EFECTOS DE SCROLL =====
function initScrollEffects() {
    // Animaciones al hacer scroll
    const animatedElements = document.querySelectorAll('.fade-in, .slide-in-left');
    
    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0) translateX(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        if (el.classList.contains('slide-in-left')) {
            el.style.transform = 'translateX(-30px)';
        } else {
            el.style.transform = 'translateY(20px)';
        }
        scrollObserver.observe(el);
    });
    
    // Smooth scroll para enlaces internos
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ===== TOOLTIPS =====
function initTooltips() {
    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ===== CARRUSEL MEJORADO =====
function initEnhancedCarousel() {
    const carousels = document.querySelectorAll('.carousel');
    
    carousels.forEach(carousel => {
        // Pausar en hover
        carousel.addEventListener('mouseenter', function() {
            const bsCarousel = bootstrap.Carousel.getInstance(this);
            if (bsCarousel) {
                bsCarousel.pause();
            }
        });
        
        carousel.addEventListener('mouseleave', function() {
            const bsCarousel = bootstrap.Carousel.getInstance(this);
            if (bsCarousel) {
                bsCarousel.cycle();
            }
        });
        
        // Indicadores personalizados
        const indicators = carousel.querySelectorAll('.carousel-indicators button');
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', function() {
                const bsCarousel = bootstrap.Carousel.getInstance(carousel);
                if (bsCarousel) {
                    bsCarousel.to(index);
                }
            });
        });
    });
}

// ===== SCROLL HORIZONTAL MEJORADO =====
function initHorizontalScroll() {
    const movieRows = document.querySelectorAll('.movie-row');
    
    movieRows.forEach(row => {
        // Botones de navegación
        const prevBtn = document.createElement('button');
        const nextBtn = document.createElement('button');
        
        prevBtn.className = 'btn btn-outline-light position-absolute start-0 top-50 translate-middle-y';
        nextBtn.className = 'btn btn-outline-light position-absolute end-0 top-50 translate-middle-y';
        
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        
        prevBtn.style.zIndex = '10';
        nextBtn.style.zIndex = '10';
        
        // Agregar botones al contenedor padre
        const container = row.parentElement;
        container.style.position = 'relative';
        container.appendChild(prevBtn);
        container.appendChild(nextBtn);
        
        // Funcionalidad de scroll
        prevBtn.addEventListener('click', () => {
            row.scrollBy({ left: -300, behavior: 'smooth' });
        });
        
        nextBtn.addEventListener('click', () => {
            row.scrollBy({ left: 300, behavior: 'smooth' });
        });
        
        // Mostrar/ocultar botones según posición
        row.addEventListener('scroll', () => {
            prevBtn.style.display = row.scrollLeft > 0 ? 'block' : 'none';
            nextBtn.style.display = row.scrollLeft < (row.scrollWidth - row.clientWidth) ? 'block' : 'none';
        });
        
        // Estado inicial
        prevBtn.style.display = 'none';
        nextBtn.style.display = row.scrollWidth > row.clientWidth ? 'block' : 'none';
    });
}

// ===== MANEJO DE ERRORES =====
function showError(message) {
    const alertContainer = document.createElement('div');
    alertContainer.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x';
    alertContainer.style.zIndex = '9999';
    alertContainer.style.marginTop = '100px';
    
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

function showSuccess(message) {
    const alertContainer = document.createElement('div');
    alertContainer.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x';
    alertContainer.style.zIndex = '9999';
    alertContainer.style.marginTop = '100px';
    
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-remover después de 3 segundos
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 3000);
}

// ===== UTILIDADES =====
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ===== MANEJO DE EVENTOS GLOBALES =====
window.addEventListener('beforeunload', function() {
    if (isLoading) {
        return 'Hay una operación en progreso. ¿Estás seguro de que quieres salir?';
    }
});

// Manejar errores JavaScript globales
window.addEventListener('error', function(event) {
    console.error('Error JavaScript:', event.error);
    // En producción, enviar error a servicio de logging
});

// ===== FUNCIONES EXPORTADAS =====
window.StreamFlix = {
    showLoading,
    hideLoading,
    showError,
    showSuccess,
    debounce,
    throttle
}; 