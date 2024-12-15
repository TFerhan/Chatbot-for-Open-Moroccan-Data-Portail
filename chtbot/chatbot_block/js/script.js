document.addEventListener('DOMContentLoaded', () => {
    const chatbotBlock = document.querySelector(".chatbot_block");
    const trbchUrl = chatbotBlock.getAttribute("data-trbch-url");
    const chatbotToggler = document.querySelector(".chatbot-toggler");
    const closeBtn = document.querySelector(".close-btn");
    const chatbox = document.querySelector(".chatbox");
    const chatInput = document.querySelector(".chat-input textarea");
    const sendChatBtn = document.querySelector(".chat-input span");
    // const languageSelection = document.querySelector(".language-selection");
    // const langBtns = document.querySelectorAll(".lang-btn");
    const loadingElement = document.querySelector(".loading");
    const menuBtn = document.querySelector('.menu-btn');
    const menuDropdown = document.querySelector('.menu-dropdown');
    const helpBtn = document.querySelector(".help-btn");
    let currentLanguage;
    let helpStep = 0;
    let helpMessages = [];
    //sss
    let isHelpGuideActive = false;

    // for feedback
    let func = "";
    let mesg = "";
    let fr_or_ar = "";

    let outcom = "";
    let lang = "";
      

    chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
    // Vérifiez que les variables d'environnement sont correctement chargées

    const API_URLS = {
        classifyIntent: "/chatbot/classify-intent",
        requestData: "/chatbot/request-data",
        generalV1: "/chatbot/general-v1"
    };

    const fr_finance_text = "Ici le lien vers toutes les 180 données correspondant au mot recherché : https://data.gov.ma/data/fr/dataset?q=finance&sort=score+desc%2C+metadata_modified+desc \nVoici un exemple parmi les résultats trouvés Titre : Finances Publiques\n Lien : https://data.gov.ma/data/fr/dataset/finances-publiques \n";
    const ar_finance_text = "إليك الرابط لجميع البيانات الـ 180 المتعلقة بالكلمة المطلوبة: https://data.gov.ma/data/ar/dataset?q=finance&sort=score+desc%2C+metadata_modified+desc \nإليك مثال من النتائج التي تم العثور عليها العنوان: المالية العامة\n الرابط: https://data.gov.ma/data/ar/dataset/finances-publiques \n";

    const email_text_fr = "Vous pouvez nous contacter par e-mail à l'adresse suivante : opendata@add.gov.ma . Si vous avez des questions, des suggestions ou besoin d'assistance, n'hésitez pas à nous écrire. Nous serons heureux de vous aider.";
    const email_text_ar = "يمكنك الاتصال بنا عبر البريد الإلكتروني على العنوان التالي: opendata@add.gov.ma . إذا كان لديك أي أسئلة أو اقتراحات أو تحتاج إلى مساعدة، فلا تتردد في الكتابة لنا. سنكون سعداء بمساعدتك.";

    

    let userMessage = null;
    const inputInitHeight = chatInput ? chatInput.scrollHeight : 0;
    // let selectedLanguage = null;

    const showLoading = () => {
        loadingElement.style.display = "block";
        chatbox.appendChild(loadingElement);
    };

    const hideLoading = () => {
        loadingElement.style.display = "none";
        if (chatbox.contains(loadingElement)) {
            chatbox.removeChild(loadingElement);
        }
    };

    

    const helpMessagesFr = [
        "Bienvenue! Voici comment utiliser le chatbot.",
        "Vous pouvez rechercher des données ou poser des questions générales sur le portail <strong> data.gov.ma </strong>. Soyez concis et précis dans vos questions en utilisant un langage clair. Cliquez sur  'Suivant' pour un exemple.",
        "Par exemple, pour demander des données, vous pouvez écrire : Je veux les données financières",
        "Ou bien une question générale : 'c'est quoi l'adresse email de contact'",
        "Merci de votre attention. N'hésitez pas à nous contacter pour tout problème ou suggestion.",


        
    ];

    const helpMessagesAr = [
        ` مرحبًا بك  
    .إليك كيفية استخدام الروبوت`,
        "يمكنك البحث عن البيانات أو طرح الأسئلة العامة على الموقع. كن موجزًا ​​ودقيقًا في أسئلتك باستخدام لغة واضحة. انقر على 'لتالي' للحصول على مثال.",
        "'على سبيل المثال لطلب البيانات يمكنك كتابة: ' أريد بيانات مالية",
        "'أو سؤال عام: 'ما هو عنوان البريد الإلكتروني للموقع",
        ".شكرًا لاهتمامك. لا تتردد في الاتصال بنا في حالة وجود أي مشكلة أو اقتراح",

    ];


    if (sendChatBtn){
        sendChatBtn.addEventListener("click", () => {
            const currentLength = chatInput.value.length;

            if (currentLength <= 1000) {
                // Envoyer le message
                handleChat();
            }
    });}

    const disableChatInput = () => {
        chatInput.disabled = true;
        sendChatBtn.disabled = true;
    };

    const enableChatInput = () => {
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
    };



    const updateInputPlaceholder = () => {
        if (currentLanguage === "Français") {
            chatInput.placeholder = "Poser une question ou retrouvez des données ...";

        } else {
            chatInput.placeholder = "اطرح سؤالاً أو ابحث عن البيانات...";
        }
    };
    const updateHelpMessages = () => {
        if (currentLanguage === "Français") {
            helpMessages = helpMessagesFr;
        } else {
            helpMessages = helpMessagesAr;
        }
    };


    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", `${className}`);
        let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined"><img src="${trbchUrl}"></span><p></p>`;
        chatLi.innerHTML = chatContent;
        chatLi.querySelector("p").innerHTML = message;

        if (currentLanguage !== "Français" ) {
            chatLi.classList.add("align-right");
        } else {
            chatLi.classList.add("align-left");
        }

        return chatLi;
    }

    const updateTextAlignment = () => {
        if (currentLanguage === "Français") {
            chatbox.classList.remove("rtl");
        } else {
            chatbox.classList.add("rtl");
        }
    };


    const feedback = async (feedbackType) => {
        try {
            if (isHelpGuideActive) return; 
            if (feedbackType === "oui") {
                func = "";
                mesg = "";
                fr_or_ar = "";
                if (currentLanguage === "Français") {
                    return "Merci pour votre retour ! Avez-vous besoin d'aide pour autre chose ?";
                } else {
                    return "شكراً لتعليقك! هل تحتاج إلى مساعدة في شيء آخر؟";
                }
            } else {
                if (func === "request_data") {
                    return await get_output_api(mesg, fr_or_ar, API_URLS.generalV1);
                } else {
                    return await get_output_api(mesg, fr_or_ar, API_URLS.requestData);
                }
            }} catch (error) {
            console.error('There was a problem with the fetch operation:', error);
            return currentLanguage === "Français" ? "Oops! Quelque chose s'est mal passé, veuillez réessayer." : "عذرًا! حدث خطأ ما، يرجى المحاولة مرة أخرى.";
            }
    };

    const handleSecondFeedback = (feedbackType) => {
        try {
            if (feedbackType === "oui") {
                if (currentLanguage === "Français") {
                    return "Merci pour votre retour !";
                } else {
                    return "شكراً لتعليقك!";
                }
            } else {
                if (currentLanguage === "Français") {
                    return  "Veuillez poser votre question dans le contexte du site uniquement. Pour plus d'informations, consultez l'aide en haut.";
                } else {
                    return  "يرجى طرح أسئلتك حول الموقع فقط. لمزيد من المعلومات، يُرجى مراجعة قسم المساعدة في الأعلى.";
                }
            }} catch (error) {
            console.error('There was a problem with the fetch operation:', error);
            return currentLanguage === "Français" ? "Oops! Quelque chose s'est mal passé, veuillez réessayer." : "عذرًا! حدث خطأ ما، يرجى المحاولة مرة أخرى.";
            }
    };




    const get_output_api = async (mesg, lang, API_URL) => {
        showLoading();
        const payload = {
            text: mesg,
            lang: lang
        };

        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        };

        try {
            const response = await fetch(API_URL, requestOptions);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            
            const data = await response.json();
            const message = data.output;
            
            const links = extractLinks(message);
            const formattedMessage = formatMessageWithLinks(message, links);
            func = "";
            mesg = "";
            fr_or_ar = "";
            hideLoading();
            return formattedMessage;}
        catch (error) {
            hideLoading();
            const errorMessage = currentLanguage === "Français" ? 
            "Oops! Quelque chose s'est mal passé, veuillez réessayer." :
            "عذرًا! حدث خطأ ما، يرجى المحاولة مرة أخرى.";
            const errorChatLi = createChatLi(errorMessage, "incoming");
            errorChatLi.classList.add("error");
            chatbox.appendChild(errorChatLi);
            console.error('There was a problem with the fetch operation:', error);
            func = "";
            mesg = "";
            fr_or_ar = "";
            return errorMessage; // Return the error message
        } finally {
            chatbox.scrollTo(0, chatbox.scrollHeight);
        }
    }




    const generateResponse = async (chatElement, language) => {
        showLoading();

        const API_URL = API_URLS.classifyIntent;
        const messageElement = chatElement.querySelector("p");
        const payload = {
            text: messageElement.textContent,
            lang: language
        };

        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        };

        try {
            const response = await fetch(API_URL, requestOptions);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            hideLoading();
            const message = data.output;
            const links = extractLinks(message);
            const formattedMessage = formatMessageWithLinks(message, links);
            const incomingChatLi = createChatLi(formattedMessage, "incoming");
            chatbox.appendChild(incomingChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);

            const feedbackRequestLi = createChatLi(currentLanguage === "Français" ? "Cette réponse a-t-elle répondu à votre demande ?" : " هل أجابت هذه الإجابة على طلبك؟", "incoming");
            const feedbackButtons = currentLanguage === "Français" ? `
                    <button class="feedback-btn" data-feedback="oui">oui</button>
                    <button class="feedback-btn" data-feedback="non">Non</button>
                ` : `
                    <button class="feedback-btn" data-feedback="oui">نعم</button>
                    <button class="feedback-btn" data-feedback="non"> لا</button>
                `;
            feedbackRequestLi.innerHTML += feedbackButtons;
            chatbox.appendChild(feedbackRequestLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
            func = data.executed_function;
            mesg = data.input_text;
            fr_or_ar = data.language;

                // Attach event listeners to feedback buttons
            document.querySelectorAll('.feedback-btn').forEach(button => {
                    button.addEventListener('click', async (event) => {
                        
                        const feedbackType = event.target.dataset.feedback;
                        event.target.parentElement.style.display = 'none';
                        const responseMessage = await feedback(feedbackType);
                        const feedbackResponseLi = createChatLi(responseMessage, "incoming");
                        chatbox.appendChild(feedbackResponseLi);
                        chatbox.scrollTo(0, chatbox.scrollHeight);
                        

                        if (feedbackType === "oui") {
                            return;
                        }

                        const secondFeedbackRequestLi = createChatLi(currentLanguage === "Français" ? "Cette réponse était-elle utile ?" : "هل كانت هذه الإجابة مفيدة؟", "incoming");
                        const secondFeedbackButtons = currentLanguage === "Français" ? `
                            <button class="second-feedback-btn" data-feedback="oui">oui</button>
                            <button class="second-feedback-btn" data-feedback="non">Non</button>
                        ` : `
                            <button class="second-feedback-btn" data-feedback="oui">نعم</button>
                            <button class="second-feedback-btn" data-feedback="non">لا</button>
                        `;
                        secondFeedbackRequestLi.innerHTML += secondFeedbackButtons;
                        chatbox.appendChild(secondFeedbackRequestLi);
                        chatbox.scrollTo(0, chatbox.scrollHeight);

                        document.querySelectorAll('.second-feedback-btn').forEach(button => {
                            button.addEventListener('click', (event) => {
                                const secondFeedbackType = event.target.dataset.feedback;
                                const secondResponseMessage = handleSecondFeedback(secondFeedbackType);
                                const secondFeedbackResponseLi = createChatLi(secondResponseMessage, "incoming");
                                chatbox.appendChild(secondFeedbackResponseLi);
                                chatbox.scrollTo(0, chatbox.scrollHeight);

                                event.target.parentElement.style.display = 'none';
                            });
                        });
                    });
                });
        } catch (error) {
            hideLoading();
            const errorMessage = currentLanguage === "Français" ? 
                "Oops! Quelque chose s'est mal passé, veuillez réessayer." :
                "عذرًا! حدث خطأ ما، يرجى المحاولة مرة أخرى.";
            console.error('There was a problem with the fetch operation:', error);
            const errorResponseLi = createChatLi(errorMessage, "incoming");
            chatbox.appendChild(errorResponseLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
        } finally {
            chatbox.scrollTo(0, chatbox.scrollHeight);
        }
    }


    const handleChat = () => {
        userMessage = chatInput.value.trim();
        if (!userMessage) return;
        chatInput.value = "";
        chatInput.style.height = `${inputInitHeight}px`;

        // Append the user's message to the chatbox
        outcom = createChatLi(userMessage, "outgoing")
        chatbox.appendChild(outcom);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        lang = currentLanguage === "Français" ? "fr" : "ar";

        generateResponse(outcom, lang);
    }

    if (chatInput){
        chatInput.addEventListener("input", () => {
            // Adjust the height of the input textarea based on its content
            chatInput.style.height = `${inputInitHeight}px`;
            chatInput.style.height = `${chatInput.scrollHeight}px`;
        });}

    if (chatInput){
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
                e.preventDefault();
                handleChat();
            }
        });}

    const extractLinks = (text) => {
        if (typeof text !== 'string') {
            console.error('Expected a string in extractLinks, but got:', typeof text);
            return [];
        }
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        let links = text.match(urlRegex);
        if (links) {
            links = links.map(link => link.endsWith('.') ? link.slice(0, -1) : link);
        }
        return links || [];
    }

    const formatMessageWithLinks = (message, links) => {
        if (!links) {
            return message;
        }
        let formattedMessage = message;
        const linkText = currentLanguage === "Français" ? "Lien" : "رابط";
        links.forEach(link => {
            formattedMessage = formattedMessage.replace(link, `<a href="${link}" target="_blank">${linkText}</a>`);
        });
        return formattedMessage;
    }

    if (sendChatBtn){
        sendChatBtn.addEventListener("click", () => {
            chatInput.style.height = `${inputInitHeight}px`;
            handleChat();
        });}

    if (chatInput){
        chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleChat();
            }
        });}

    if (closeBtn){
        closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));}



    const clearChatbox = () => {
        chatbox.innerHTML = "";
    }

    // langBtns.forEach(btn => {
    //     btn.addEventListener("click", (e) => {
    //         selectedLanguage = e.target.dataset.lang;
    //         languageSelection.style.display = "none"; // Hide language selection
            
    //         // Show chatbox
    //         document.querySelector('.chatbox').classList.add('show'); // Add "show" class to chatbox
    //         chatInput.parentElement.style.display = "flex"; // Show chat input
    //         clearChatbox();
    //         helpStep = 0;

    //         // Welcome message logic
    //         const welcomeMessage = selectedLanguage === "fr" ? 
    //             "Bonjour 👋<br>Comment puis-je vous aider ? Je suis là pour vous assister dans <strong>la recherche de données </strong> et pour <strong>répondre à vos questions</strong> sur le portail <strong> data.gov.ma </strong>. Veuillez formuler votre demande de manière précise afin que je puisse vous fournir une assistance efficace." : 
    //             "مرحبا 👋<br>كيف يمكنني مساعدتك؟ أنا هنا لمساعدتك في البحث عن البيانات والرد على أسئلتك العامة المتعلقة بالموقع. يرجى تنسيق طلباتك بوضوح للحصول على مساعدة فعالة."; 
            
    //         const welcomeChatLi = createChatLi(welcomeMessage, "incoming"); 
    //         chatbox.appendChild(welcomeChatLi); 
    //         chatbox.scrollTo(0, chatbox.scrollHeight); 
    //     }); 
    // });
    
    menuBtn.addEventListener('click', (event) => {
            console.log("Menu button clicked");
            event.stopPropagation(); // Prevent the click from bubbling up to the document
            menuDropdown.style.display = menuDropdown.style.display === 'block' ? 'none' : 'block';
    });

        // Hide the menu dropdown when clicking outside of it
    document.addEventListener('click', (event) => {
            if (!menuDropdown.contains(event.target) && !menuBtn.contains(event.target)) {
                menuDropdown.style.display = 'none';
            }
    });

        
    helpBtn.addEventListener("click", () => {
            menuDropdown.style.display = 'none'; // Close the menu dropdown
            showHelpMessage(); // Show the help message
    });
            // Vous pouvez remplacer cette alerte par la logique que vous souhaitez
        
    // });
    // Sélectionner les éléments nécessaires

    // const addSwitchLanguageBtn = () => {
    //     // Vérifier si le bouton existe déjà
    //     let switchLangBtn = document.getElementById("switch-lang-btn");
    //     if (!switchLangBtn) {
    //         switchLangBtn = document.createElement("button");
    //         switchLangBtn.id = "switch-lang-btn";
    //         menuDropdown.appendChild(switchLangBtn);
    //     }
    //     switchLangBtn.textContent = currentLanguage === "Français" ? "عربي" : "Français";

    //     // Supprimer les anciens gestionnaires d'événements pour éviter les doublons
    //     switchLangBtn.removeEventListener("click", switchLanguageHandler);

    //     // Ajouter un nouveau gestionnaire d'événements
    //     switchLangBtn.addEventListener("click", switchLanguageHandler);
    // };

    // const switchLanguageHandler = () => {
    //     // Basculer la langue
    //     currentLanguage = currentLanguage === "Français" ? "عربي" : "Français";
    //     // Mettre à jour le texte du bouton
    //     const switchLangBtn = document.getElementById("switch-lang-btn");
    //     switchLangBtn.textContent = currentLanguage === "Français" ? "عربي" : "Français";

    //     // Simuler un clic sur le bouton de langue correspondant
    //     const targetLangBtn = Array.from(langBtns).find(btn => btn.textContent === currentLanguage);
    //     if (targetLangBtn) {
    //         targetLangBtn.click();
    //     }
    // };

    // // Ajouter des gestionnaires d'événements pour les boutons de langue
    // langBtns.forEach(btn => {
    //     btn.addEventListener("click", () => {
    //         currentLanguage = btn.textContent;
            
    //         updateTextAlignment();
    //         addSwitchLanguageBtn();
    //         updateHelpMessages();
    //         updateInputPlaceholder();
            
            
            
    //         // Masquer le widget de sélection de langue et afficher la chatbox
    //         helpStep = 0;

    //         languageSelection.style.display = "none";
    //         chatbox.style.display = "flex";
    //     });
    // });


    // Fonction pour afficher le message d'aide avec un bouton "Suivant"
    const showHelpMessage = () => {
        disableChatInput();
        console.log("show help message : ", helpStep);
        isHelpGuideActive = true;
        // helpStep = 0;
        const helpChatLi = createChatLi(helpMessages[helpStep], "incoming");
        const nextButton = document.createElement("button");
        nextButton.textContent = currentLanguage === "Français" ? "Suivant" : "التالي";
        nextButton.classList.add("next-btn");
        nextButton.addEventListener("click", (event) => {
            event.target.style.display = 'none';
            showNextHelpMessage();
            // Cachez le bouton après qu'il ait été cliqué
        });
        helpChatLi.appendChild(nextButton);
        chatbox.appendChild(helpChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
    }

    // Fonction pour afficher les messages suivants et simuler l'entrée de texte et l'envoi
    const showNextHelpMessage = () => {
        if (isHelpGuideActive) {
            helpStep++;
            console.log("show next help message : ", helpStep);
            if (helpStep <= helpMessages.length) {
                const helpChatLi = createChatLi(helpMessages[helpStep], "incoming");
                const nextButton = document.createElement("button");
                nextButton.textContent = currentLanguage === "Français" ? "Suivant" : "التالي";
                nextButton.classList.add("next-btn");
                nextButton.addEventListener("click", (event) => {
                    event.target.style.display = 'none';
                    showNextHelpMessage();
                    // Cachez le bouton après qu'il ait été cliqué
                });
                helpChatLi.appendChild(nextButton);
                chatbox.appendChild(helpChatLi);
                chatbox.scrollTo(0, chatbox.scrollHeight);

                if (helpStep === 2) {
                    nextButton.style.display = 'none';
                    setTimeout(() => {
                        const helpChatout = createChatLi(currentLanguage === "Français" ? "Je veux les données de la finance" : "أريد بيانات المالية", "outgoing");
                        chatbox.appendChild(helpChatout);
                        chatbox.scrollTo(0, chatbox.scrollHeight);

                        const links_fr_ex = extractLinks(fr_finance_text);
                        const formattedMessage_fr_ex = formatMessageWithLinks(fr_finance_text, links_fr_ex);

                        const links_ar_ex = extractLinks(ar_finance_text);
                        const formattedMessage_ar_ex = formatMessageWithLinks(ar_finance_text, links_ar_ex);

                        const helpChatLi = createChatLi(currentLanguage === "Français" ? formattedMessage_fr_ex : formattedMessage_ar_ex, "incoming");
                        chatbox.appendChild(helpChatLi);
                        chatbox.scrollTo(0, chatbox.scrollHeight);

                        setTimeout(() => {
                            showNextHelpMessage();
                        }, 5000);
                    }, 4000);
                } else if (helpStep === 3) {
                    nextButton.style.display = 'none';
                    setTimeout(() => {
                        const helpChatout = createChatLi(currentLanguage === "Français" ? "C'est quoi l'adresse email de contact" : "ما هو عنوان البريد الإلكتروني للموقع", "outgoing");
                        chatbox.appendChild(helpChatout);
                        chatbox.scrollTo(0, chatbox.scrollHeight);

                        setTimeout(() => {
                            const helpChatLi = createChatLi(currentLanguage === "Français" ? email_text_fr : email_text_ar, "incoming");
                            chatbox.appendChild(helpChatLi);
                            chatbox.scrollTo(0, chatbox.scrollHeight);

                            setTimeout(() => {
                                showNextHelpMessage();
                            }, 5000);
                        }, 5000);
                    }, 4000);
                } else if (helpStep === 4) {
                    nextButton.textContent = currentLanguage === "Français" ? "Terminer" : "النهاية";
                    nextButton.style.display = 'none';
                    isHelpGuideActive = false;
                    helpStep = 0;
                    enableChatInput();
                    return;
                }
            }
        }
    }

    const debounce = (func, delay) => {
        let timeoutId;
        return (...args) => {
            if (timeoutId) {
                clearTimeout(timeoutId);
            }
            timeoutId = setTimeout(() => {
                func.apply(null, args);
            }, delay);
        };
    };

    if (chatInput){
        chatInput.addEventListener("input", debounce(() => {
            chatInput.style.height = `${inputInitHeight}px`;
            chatInput.style.height = `${chatInput.scrollHeight}px`;
        }, 300));}


    const toggleChatInput = (isDisabled) => {
        chatInput.disabled = isDisabled;
        sendChatBtn.disabled = isDisabled;
        if (isDisabled) {
            chatInput.classList.add("disabled");
            sendChatBtn.classList.add("disabled");
        } else {
            chatInput.classList.remove("disabled");
            sendChatBtn.classList.remove("disabled");
        }
    };

    // Call this function when the help guide is activated
    const activateHelpGuide = () => {
        isHelpGuideActive = true;
        toggleChatInput(true);
        // Additional logic to start the help guide
    };

    // Call this function when the help guide is deactivated
    const deactivateHelpGuide = () => {
        isHelpGuideActive = false;
        toggleChatInput(false);
        // Additional logic to end the help guide
    };

    (function ($, Drupal, drupalSettings) {
        
        var drupal_lang = drupalSettings.chatbot_block.languageCode;
        currentLanguage = drupal_lang === "fr" ? "Français" : "عربي";
                    
            // Show chatbox
        document.querySelector('.chatbox').classList.add('show'); // Add "show" class to chatbox
        chatInput.parentElement.style.display = "flex"; // Show chat input
        // clearChatbox();
        helpStep = 0;
        

        // Welcome message logic
        const welcomeMessage = drupal_lang === "fr" ? 
            "Bonjour 👋<br>Comment puis-je vous aider ? Je suis là pour vous assister dans <strong>la recherche de données </strong> et pour <strong>répondre à vos questions</strong> sur le portail <strong> data.gov.ma </strong>. Veuillez formuler votre demande de manière précise afin que je puisse vous fournir une assistance efficace." : 
            "مرحبا 👋<br>كيف يمكنني مساعدتك؟ أنا هنا لمساعدتك في البحث عن البيانات والرد على أسئلتك العامة المتعلقة بالموقع. يرجى تنسيق طلباتك بوضوح للحصول على مساعدة فعالة."; 
        
        const welcomeChatLi = createChatLi(welcomeMessage, "incoming"); 
        chatbox.appendChild(welcomeChatLi); 
        chatbox.scrollTo(0, chatbox.scrollHeight); 

        updateTextAlignment();
        // addSwitchLanguageBtn();
        updateHelpMessages();
        updateInputPlaceholder();
        
        
        
        helpStep = 0;
        chatbox.style.display = "flex";
      
    })(jQuery, Drupal, drupalSettings);
});
