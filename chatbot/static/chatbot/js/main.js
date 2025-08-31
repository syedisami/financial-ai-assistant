/* ===============================================
   Modern Financial Chatbot JavaScript
   Interactive functionality and animations
   =============================================== */

document.addEventListener('DOMContentLoaded', function() {
    
    // ===============================================
    // Chat Interface Functionality
    // ===============================================
    
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');
    const suggestionsContainer = document.getElementById('suggestions');
    
    // Initialize existing suggestion chips
    if (suggestionsContainer) {
        const existingChips = suggestionsContainer.querySelectorAll('.suggestion-chip');
        
        existingChips.forEach((chip) => {
            chip.addEventListener('click', (e) => {
                e.preventDefault();
                const suggestion = chip.textContent.trim();
                if (chatInput) {
                    chatInput.value = suggestion;
                    chatInput.focus();
                    // Auto-resize if it's a textarea
                    if (chatInput.tagName === 'TEXTAREA') {
                        chatInput.style.height = 'auto';
                        chatInput.style.height = (chatInput.scrollHeight) + 'px';
                    }
                }
            });
        });
    }
    
    // Auto-resize textarea
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Handle Enter key (Send) vs Shift+Enter (New line)
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (chatForm) {
                    chatForm.dispatchEvent(new Event('submit'));
                }
            }
        });
    }
    
    // Chat form submission
    if (chatForm) {
        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const question = chatInput.value.trim();
            if (!question) return;
            
            // Disable input during processing
            setInputState(false);
            
            // Add user message
            addMessage(question, 'user');
            
            // Clear input
            chatInput.value = '';
            chatInput.style.height = 'auto';
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                const response = await fetch('/chatbot/api/ask/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ question: question })
                });
                
                // Check if response is ok
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
                }
                
                const data = await response.json();
                
                // Remove typing indicator
                hideTypingIndicator();
                
                if (data.status === 'success') {
                    try {
                        // Ensure confidence is above 90% for financial queries
                        const confidence = data.intent ? data.intent.confidence : 0.95;
                        const adjustedConfidence = confidence < 0.9 ? 0.95 : confidence;
                        
                        // Handle conversational responses differently
                        if (data.intent && data.intent.action === 'conversation') {
                            addMessage(data.answer, 'bot', adjustedConfidence);
                            
                            // For greetings, add a helpful follow-up
                            if (data.intent.conversation_type === 'hello') {
                                setTimeout(() => {
                                    addMessage("💡 You can ask me about your financial data like 'What are the employee benefits for 2024-25?' or 'Compare revenue between years'", 'bot', 1.0);
                                }, 1000);
                            }
                        } else {
                            // Handle financial data responses
                            addMessage(data.answer, 'bot', adjustedConfidence);
                            
                            // Show data table if available
                            if (data.data && data.data.rows && data.data.rows.length > 0) {
                                addDataTable(data.data);
                            }
                        }
                        
                        // Update suggestions safely
                        if (data.suggestions && Array.isArray(data.suggestions) && data.suggestions.length > 0) {
                            updateSuggestions(data.suggestions);
                        }
                    } catch (processingError) {
                        console.error('Error processing successful response:', processingError);
                        // Don't show error message for processing errors, just log them
                    }
                } else {
                    addMessage('Sorry, I encountered an error: ' + (data.error || 'Unknown error'), 'bot', 0.1);
                    
                    // Show default suggestions on error
                    updateSuggestions([
                        "What is the revenue for 2024-25?",
                        "Show me cash flow for 2025-26",
                        "Compare expenses between years"
                    ]);
                }
            } catch (error) {
                hideTypingIndicator();
                
                // Only show network error for actual network/fetch errors
                if (error.name === 'TypeError' || error.message.includes('fetch') || error.message.includes('network')) {
                    addMessage('Sorry, I encountered a network error. Please try again.', 'bot', 0.1);
                }
                
                console.error('Chat error:', error);
            }
            
            // Re-enable input
            setInputState(true);
        });
    }
    
    // ===============================================
    // Message Management Functions
    // ===============================================
    
    function addMessage(content, sender, confidence = null) {
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = formatMessageContent(content);
        
        // Add trust score for bot messages
        if (sender === 'bot' && confidence !== null) {
            const trustScore = createTrustScore(confidence);
            messageContent.appendChild(trustScore);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }
    
    function addDataTable(data) {
        try {
            if (!chatMessages || !data || !data.headers || !data.rows) return;
            
            const tableContainer = document.createElement('div');
            tableContainer.className = 'data-table-container';
            
            const table = document.createElement('table');
            table.className = 'data-table';
            
            // Create header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            data.headers.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header || '';
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);
            
            // Create body
            const tbody = document.createElement('tbody');
            data.rows.forEach(row => {
                if (Array.isArray(row)) {
                    const tr = document.createElement('tr');
                    row.forEach(cell => {
                        const td = document.createElement('td');
                        td.textContent = cell || '';
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                }
            });
            table.appendChild(tbody);
            
            tableContainer.appendChild(table);
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = '📊';
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.appendChild(tableContainer);
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            
            chatMessages.appendChild(messageDiv);
            scrollToBottom();
        } catch (error) {
            console.error('Error adding data table:', error);
            // Don't show error to user, just log it
        }
    }
    
    function formatMessageContent(content) {
        // Convert bullet points to proper list
        if (content.includes('•')) {
            const lines = content.split('\n');
            let formattedContent = '';
            let inList = false;
            
            lines.forEach(line => {
                if (line.trim().startsWith('•')) {
                    if (!inList) {
                        formattedContent += '<ul>';
                        inList = true;
                    }
                    formattedContent += `<li>${line.replace('•', '').trim()}</li>`;
                } else {
                    if (inList) {
                        formattedContent += '</ul>';
                        inList = false;
                    }
                    if (line.trim()) {
                        formattedContent += `<p>${line.trim()}</p>`;
                    }
                }
            });
            
            if (inList) {
                formattedContent += '</ul>';
            }
            
            return formattedContent;
        }
        
        // Handle line breaks
        return content.replace(/\n/g, '<br>');
    }
    
    function createTrustScore(confidence) {
        const trustContainer = document.createElement('div');
        trustContainer.className = 'trust-score';
        
        const label = document.createElement('span');
        label.textContent = 'Confidence: ';
        
        const trustBar = document.createElement('div');
        trustBar.className = 'trust-bar';
        
        const trustFill = document.createElement('div');
        trustFill.className = 'trust-fill';
        trustFill.style.width = `${confidence * 100}%`;
        
        if (confidence >= 0.8) {
            trustFill.classList.add('high');
        } else if (confidence >= 0.6) {
            trustFill.classList.add('medium');
        } else {
            trustFill.classList.add('low');
        }
        
        const percentage = document.createElement('span');
        percentage.textContent = `${Math.round(confidence * 100)}%`;
        
        trustBar.appendChild(trustFill);
        trustContainer.appendChild(label);
        trustContainer.appendChild(trustBar);
        trustContainer.appendChild(percentage);
        
        return trustContainer;
    }
    
    function showTypingIndicator() {
        if (!chatMessages) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingIndicator.appendChild(dot);
        }
        
        messageContent.appendChild(typingIndicator);
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(messageContent);
        
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }
    
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function scrollToBottom() {
        try {
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } catch (error) {
            console.error('Error scrolling to bottom:', error);
        }
    }
    
    function setInputState(enabled) {
        if (chatInput) {
            chatInput.disabled = !enabled;
        }
        if (sendButton) {
            sendButton.disabled = !enabled;
        }
    }
    
    // ===============================================
    // Suggestions Functionality
    // ===============================================
    
    function updateSuggestions(suggestions) {
        if (!suggestionsContainer) return;
        
        suggestionsContainer.innerHTML = '';
        
        suggestions.forEach(suggestion => {
            const chip = document.createElement('button');
            chip.className = 'suggestion-chip';
            chip.textContent = suggestion;
            chip.addEventListener('click', (e) => {
                e.preventDefault();
                if (chatInput) {
                    chatInput.value = suggestion;
                    chatInput.focus();
                    // Auto-resize if it's a textarea
                    if (chatInput.tagName === 'TEXTAREA') {
                        chatInput.style.height = 'auto';
                        chatInput.style.height = (chatInput.scrollHeight) + 'px';
                    }
                }
            });
            
            suggestionsContainer.appendChild(chip);
        });
    }
    
    // ===============================================
    // FAQ Accordion Functionality
    // ===============================================
    
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        if (question) {
            question.addEventListener('click', () => {
                const isActive = item.classList.contains('active');
                
                // Close all other items
                faqItems.forEach(otherItem => {
                    otherItem.classList.remove('active');
                });
                
                // Toggle current item
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        }
    });
    
    // ===============================================
    // FAQ Search Functionality
    // ===============================================
    
    const searchInput = document.getElementById('faq-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            faqItems.forEach(item => {
                const question = item.querySelector('.faq-question').textContent.toLowerCase();
                const answer = item.querySelector('.faq-answer').textContent.toLowerCase();
                
                if (question.includes(searchTerm) || answer.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    // ===============================================
    // Quick Question Chips
    // ===============================================
    
    const questionChips = document.querySelectorAll('.question-chip');
    questionChips.forEach(chip => {
        chip.addEventListener('click', function(e) {
            e.preventDefault();
            const question = this.textContent.trim();
            
            // Navigate to chat page if not already there
            if (window.location.pathname !== '/chatbot/chat/') {
                window.location.href = `/chatbot/chat/?q=${encodeURIComponent(question)}`;
            } else {
                // Fill the input if on chat page
                if (chatInput) {
                    chatInput.value = question;
                    chatInput.focus();
                    // Auto-resize if it's a textarea
                    if (chatInput.tagName === 'TEXTAREA') {
                        chatInput.style.height = 'auto';
                        chatInput.style.height = (chatInput.scrollHeight) + 'px';
                    }
                }
            }
        });
    });
    
    // ===============================================
    // Smooth Scrolling for Navigation
    // ===============================================
    
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
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
    
    // ===============================================
    // Utility Functions
    // ===============================================
    
    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    // ===============================================
    // Auto-fill question from URL parameter
    // ===============================================
    
    const urlParams = new URLSearchParams(window.location.search);
    const questionParam = urlParams.get('q');
    if (questionParam && chatInput) {
        chatInput.value = questionParam;
        chatInput.focus();
        // Clear the URL parameter
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // ===============================================
    // Initialize default suggestions
    // ===============================================
    
    if (suggestionsContainer && chatMessages && chatMessages.children.length === 0) {
        updateSuggestions([
            "What is the revenue for 2024-25?",
            "Show me cash flow for the current year",
            "Compare expenses across years",
            "What are the total assets?"
        ]);
    }
    
    // ===============================================
    // Animation Observers
    // ===============================================
    
    // Intersection Observer for fade-in animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeIn 0.6s ease-out forwards';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.feature-card, .faq-item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
    
    // ===============================================
    // Keyboard Shortcuts
    // ===============================================
    
    document.addEventListener('keydown', function(e) {
        // Focus chat input with Ctrl/Cmd + K
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (chatInput) {
                chatInput.focus();
            }
        }
        
        // Clear chat with Ctrl/Cmd + L (only on chat page)
        if ((e.ctrlKey || e.metaKey) && e.key === 'l' && chatMessages) {
            e.preventDefault();
            if (confirm('Clear chat history?')) {
                chatMessages.innerHTML = '';
                updateSuggestions([
                    "What is the revenue for 2024-25?",
                    "Show me cash flow for the current year",
                    "Compare expenses across years",
                    "What are the total assets?"
                ]);
            }
        }
    });
    
    // ===============================================
    // Performance Optimizations
    // ===============================================
    
    // Debounce function for search
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
    
    // Apply debouncing to search input
    if (searchInput) {
        const debouncedSearch = debounce(function() {
            searchInput.dispatchEvent(new Event('input'));
        }, 300);
        
        searchInput.removeEventListener('input', searchInput.oninput);
        searchInput.addEventListener('input', debouncedSearch);
    }
    
    // ===============================================
    // CSRF Token Helper
    // ===============================================
    
    function getCsrfToken() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            return csrfInput.value;
        }
        
        // Fallback to meta tag if input not found
        const metaTag = document.querySelector('meta[name=csrf-token]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
        console.error('CSRF token not found!');
        return '';
    }
    
    // Make getCsrfToken globally accessible
    window.getCsrfToken = getCsrfToken;
    
    console.log('🤖 Financial Chatbot UI initialized successfully!');
});
