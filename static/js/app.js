const app = Vue.createApp({
    data() {
        return {
            loading: false,
            services: [],
            cart: [],
            user: null,
            addresses: [],
            selectedAddress: null,
            pickupDate: null,
            showAddressModal: false,
            showLoginModal: false,
            notifications: [],
            orderHistory: [],
            currentStep: 1,
            paymentProcessing: false,
            formErrors: {},
        }
    },
    computed: {
        cartTotal() {
            return this.cart.reduce((total, item) => total + (item.quantity * item.price), 0).toFixed(2)
        },
        isAuthenticated() {
            return this.user !== null
        }
    },
    methods: {
        async fetchServices() {
            try {
                this.loading = true
                const response = await fetch('/api/services')
                this.services = await response.json()
            } catch (error) {
                this.showNotification('Error loading services', 'error')
            } finally {
                this.loading = false
            }
        },
        addToCart(service) {
            const existingItem = this.cart.find(item => item.id === service.id)
            if (existingItem) {
                existingItem.quantity++
            } else {
                this.cart.push({...service, quantity: 1})
            }
            this.showNotification('Item added to cart', 'success')
        },
        async processPayment() {
            if (!this.isAuthenticated) {
                this.showLoginModal = true
                return
            }
            
            try {
                this.paymentProcessing = true
                const response = await fetch('/api/payment/mpesa', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        amount: this.cartTotal,
                        phone: this.user.phone_number,
                        order_id: this.currentOrderId
                    })
                })
                
                const result = await response.json()
                if (result.success) {
                    this.showNotification('Please check your phone for the STK push', 'success')
                    this.startPaymentStatusCheck(result.checkout_request_id)
                } else {
                    this.showNotification(result.message, 'error')
                }
            } catch (error) {
                this.showNotification('Payment processing failed', 'error')
            } finally {
                this.paymentProcessing = false
            }
        },
        async startPaymentStatusCheck(checkoutRequestId) {
            const checkStatus = async () => {
                try {
                    const response = await fetch(`/api/payment/status/${checkoutRequestId}`)
                    const result = await response.json()
                    
                    if (result.status === 'completed') {
                        this.showNotification('Payment successful!', 'success')
                        this.currentStep = 4  // Move to confirmation step
                        return
                    } else if (result.status === 'failed') {
                        this.showNotification('Payment failed. Please try again.', 'error')
                        return
                    }
                    
                    // Continue checking if pending
                    setTimeout(checkStatus, 5000)
                } catch (error) {
                    this.showNotification('Error checking payment status', 'error')
                }
            }
            
            checkStatus()
        },
        showNotification(message, type = 'info') {
            const id = Date.now()
            this.notifications.push({ id, message, type })
            setTimeout(() => {
                this.notifications = this.notifications.filter(n => n.id !== id)
            }, 5000)
        },
        async submitOrder() {
            try {
                if (!this.validateOrder()) return
                
                const response = await fetch('/api/orders', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        items: this.cart,
                        address_id: this.selectedAddress,
                        pickup_date: this.pickupDate,
                    })
                })
                
                const result = await response.json()
                if (result.success) {
                    this.currentOrderId = result.order_id
                    this.currentStep = 3  // Move to payment step
                } else {
                    this.showNotification(result.message, 'error')
                }
            } catch (error) {
                this.showNotification('Error submitting order', 'error')
            }
        },
        validateOrder() {
            this.formErrors = {}
            
            if (!this.selectedAddress) {
                this.formErrors.address = 'Please select a delivery address'
            }
            if (!this.pickupDate) {
                this.formErrors.pickupDate = 'Please select a pickup date'
            }
            if (this.cart.length === 0) {
                this.formErrors.cart = 'Your cart is empty'
            }
            
            return Object.keys(this.formErrors).length === 0
        }
    },
    mounted() {
        this.fetchServices()
        
        // Add smooth scroll animation
        AOS.init({
            duration: 800,
            easing: 'ease-in-out'
        })
        
        document.addEventListener('DOMContentLoaded', function() {
            // Mobile menu toggle
            const menuButton = document.querySelector('.mobile-menu-button');
            const navMenu = document.querySelector('.nav-menu');
            
            if (menuButton) {
                menuButton.addEventListener('click', function() {
                    navMenu.classList.toggle('active');
                });
            }
            
            // Smooth scrolling for all anchor links
            document.addEventListener('click', function(e) {
                if (e.target.tagName === 'A' && e.target.hash) {
                    e.preventDefault();
                    const targetId = e.target.hash;
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        targetElement.scrollIntoView({ behavior: 'smooth' });
                        // Close mobile menu if open
                        navMenu.classList.remove('active');
                    }
                }
            });
            
            // Lazy load images
            if ('loading' in HTMLImageElement.prototype) {
                const images = document.querySelectorAll('img[loading="lazy"]');
                images.forEach(img => {
                    img.src = img.dataset.src;
                });
            } else {
                // Fallback for browsers that don't support lazy loading
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
                document.body.appendChild(script);
            }
            
            // Form validation
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                form.addEventListener('submit', function(e) {
                    if (!form.checkValidity()) {
                        e.preventDefault();
                        const firstInvalid = form.querySelector(':invalid');
                        if (firstInvalid) {
                            firstInvalid.focus();
                        }
                    }
                });
            });
        });

        // Navbar scroll behavior
        const navbar = document.querySelector('.navbar');
        let lastScroll = 0;

        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll <= 0) {
                navbar.style.transform = 'translateY(0)';
                return;
            }
            
            if (currentScroll > lastScroll && !navbar.classList.contains('scroll-down')) {
                // Scroll down
                navbar.style.transform = 'translateY(-100%)';
                navbar.classList.add('scroll-down');
            } else if (currentScroll < lastScroll && navbar.classList.contains('scroll-down')) {
                // Scroll up
                navbar.style.transform = 'translateY(0)';
                navbar.classList.remove('scroll-down');
            }
            
            lastScroll = currentScroll;
        });

        // Scroll animations
        const scrollElements = document.querySelectorAll("[data-scroll]");

        const elementInView = (el, dividend = 1) => {
            const elementTop = el.getBoundingClientRect().top;
            return (
                elementTop <=
                (window.innerHeight || document.documentElement.clientHeight) / dividend
            );
        };

        const displayScrollElement = (element) => {
            element.classList.add("in-view");
        };

        const hideScrollElement = (element) => {
            element.classList.remove("in-view");
        };

        const handleScrollAnimation = () => {
            scrollElements.forEach((el) => {
                if (elementInView(el, 1.25)) {
                    displayScrollElement(el);
                } else {
                    hideScrollElement(el);
                }
            });
        };

        window.addEventListener('scroll', () => {
            handleScrollAnimation();
        });

        // Initialize animations on load
        window.addEventListener('load', () => {
            handleScrollAnimation();
        });

        // Price calculator (example functionality)
        const calculatePrice = (weight, service) => {
            const basePrices = {
                'basic': 500,
                'premium': 1000,
                'express': 1500
            };
            
            return basePrices[service] * weight;
        };
    }
})
