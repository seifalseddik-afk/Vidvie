// ===== AI Tutor Module =====
// Built-in Arabic language knowledge base for offline AI tutoring

// ===== Knowledge Base =====
const ARABIC_KNOWLEDGE = {
    // Grammar rules
    grammar: {
        'الفاعل': 'الفاعل هو الاسم المرفوع الذي يدل على من قام بالفعل. يأتي بعد الفعل في الجملة الفعلية.\n\nعلامات رفع الفاعل:\n- الضمة: إذا كان مفرداً أو جمع تكسير أو جمع مؤنث سالم (كتبَ الطالبُ)\n- الألف: إذا كان مثنى (جاءَ الطالبانِ)\n- الواو: إذا كان جمع مذكر سالم (نجحَ المعلمونَ)\n\nمثال: كتبَ الطالبُ الدرسَ ← الفاعل: الطالبُ (مرفوع بالضمة)',
        'المفعول به': 'المفعول به هو الاسم المنصوب الذي يقع عليه فعل الفاعل.\n\nعلامات نصب المفعول به:\n- الفتحة: إذا كان مفرداً أو جمع تكسير (قرأتُ الكتابَ)\n- الياء: إذا كان مثنى أو جمع مذكر سالم (رأيتُ المعلمَيْنِ)\n- الكسرة: إذا كان جمع مؤنث سالم (شكرتُ المعلماتِ)\n\nمثال: كتبَ الطالبُ الدرسَ ← المفعول به: الدرسَ (منصوب بالفتحة)',
        'المبتدأ': 'المبتدأ هو الاسم المرفوع الذي تبدأ به الجملة الاسمية. يكون مرفوعاً دائماً.\n\nمثال: الطقسُ جميلٌ ← المبتدأ: الطقسُ\nالمعلمُ نشيطٌ ← المبتدأ: المعلمُ',
        'الخبر': 'الخبر هو الجزء الذي يُكمل معنى المبتدأ في الجملة الاسمية. يكون مرفوعاً.\n\nأنواع الخبر:\n1. خبر مفرد: الطالبُ مجتهدٌ\n2. خبر جملة فعلية: الطالبُ يدرسُ\n3. خبر جملة اسمية: الحديقةُ أزهارُها جميلةٌ\n4. خبر شبه جملة: الكتابُ على الطاولةِ',
        'الجملة الاسمية': 'الجملة الاسمية هي التي تبدأ باسم. تتكون من مبتدأ وخبر.\n\nأمثلة:\n- العلمُ نورٌ (المبتدأ: العلمُ ، الخبر: نورٌ)\n- السماءُ صافيةٌ (المبتدأ: السماءُ ، الخبر: صافيةٌ)\n- الطلابُ مجتهدونَ (المبتدأ: الطلابُ ، الخبر: مجتهدونَ)',
        'الجملة الفعلية': 'الجملة الفعلية هي التي تبدأ بفعل. تتكون من فعل + فاعل + مفعول به (إن وُجد).\n\nأمثلة:\n- كتبَ الطالبُ الدرسَ (فعل + فاعل + مفعول به)\n- ذهبَ الولدُ (فعل + فاعل)\n- نامَ الطفلُ باكراً (فعل + فاعل + ظرف)',
        'الفعل الماضي': 'الفعل الماضي يدل على حدث وقع في الزمن الماضي.\n\nعلامته: يقبل تاء التأنيث الساكنة (كتبَتْ) وتاء الفاعل (كتبْتُ).\n\nأمثلة: كتبَ ، ذهبَ ، قرأَ ، أكلَ ، شربَ ، لعبَ\n\nبناء الفعل الماضي:\n- مبني على الفتح: كتبَ\n- مبني على السكون (مع الضمائر): كتبْتُ\n- مبني على الضم (مع واو الجماعة): كتبُوا',
        'الفعل المضارع': 'الفعل المضارع يدل على حدث يقع الآن أو في المستقبل.\n\nعلامته: يبدأ بأحد حروف المضارعة (أ ن ي ت) المجموعة في كلمة "أَنَيْتُ".\n\nأمثلة: يكتبُ ، أذهبُ ، نقرأُ ، تلعبُ\n\nإعرابه:\n- مرفوع بالضمة: يكتبُ الطالبُ\n- منصوب بالفتحة بعد أن/لن: لن يكتبَ\n- مجزوم بالسكون بعد لم/لا الناهية: لم يكتبْ',
        'فعل الأمر': 'فعل الأمر يدل على طلب القيام بعمل.\n\nطريقة تكوينه: نأخذ الفعل المضارع → نحذف حرف المضارعة → نسكّن الآخر.\n\nأمثلة:\nيَكتُبُ → اُكتُبْ\nيَذهَبُ → اِذهَبْ\nيَقرأُ → اِقرَأْ\nيَأكُلُ → كُلْ\n\nفعل الأمر مبني دائماً.',
        'الحال': 'الحال هو اسم منصوب يبين هيئة الفاعل أو المفعول به عند وقوع الفعل.\n\nأمثلة:\n- جاءَ الطالبُ مسروراً (الحال: مسروراً - يبين حال الطالب)\n- شربتُ الماءَ بارداً (الحال: بارداً - يبين حال الماء)\n\nالحال يكون دائماً منصوباً ونكرة.',
        'النعت': 'النعت (الصفة) هو اسم يصف اسماً قبله ويتبعه في الإعراب والتعريف والتنكير والتذكير والتأنيث والعدد.\n\nأمثلة:\n- قرأتُ كتاباً مفيداً (نعت منصوب)\n- جاءَ الطالبُ المجتهدُ (نعت مرفوع)\n- مررتُ بالرجلِ الطويلِ (نعت مجرور)',
        'المضاف إليه': 'المضاف إليه هو اسم مجرور يأتي بعد المضاف ليتمم معناه.\n\nقواعد الإضافة:\n- المضاف إليه مجرور دائماً\n- المضاف يُحذف منه التنوين\n- المضاف لا يقبل "أل" التعريف\n\nأمثلة:\n- كتابُ الطالبِ (المضاف: كتابُ ، المضاف إليه: الطالبِ)\n- بابُ المدرسةِ (المضاف: بابُ ، المضاف إليه: المدرسةِ)'
    },

    // Parsing (إعراب)
    parsing: {
        'ذهب الولد إلى المدرسة': 'إعراب: ذهبَ الولدُ إلى المدرسةِ\n\n• ذهبَ: فعل ماضٍ مبني على الفتح\n• الولدُ: فاعل مرفوع وعلامة رفعه الضمة الظاهرة\n• إلى: حرف جر مبني على السكون\n• المدرسةِ: اسم مجرور بـ"إلى" وعلامة جره الكسرة الظاهرة',
        'كتب الطالب الدرس': 'إعراب: كتبَ الطالبُ الدرسَ\n\n• كتبَ: فعل ماضٍ مبني على الفتح\n• الطالبُ: فاعل مرفوع وعلامة رفعه الضمة الظاهرة\n• الدرسَ: مفعول به منصوب وعلامة نصبه الفتحة الظاهرة',
        'الطالب مجتهد': 'إعراب: الطالبُ مجتهدٌ\n\n• الطالبُ: مبتدأ مرفوع وعلامة رفعه الضمة الظاهرة\n• مجتهدٌ: خبر مرفوع وعلامة رفعه الضمة الظاهرة',
        'العلم نور': 'إعراب: العلمُ نورٌ\n\n• العلمُ: مبتدأ مرفوع وعلامة رفعه الضمة الظاهرة\n• نورٌ: خبر مرفوع وعلامة رفعه الضمة الظاهرة',
        'قرأت الطالبة القصة': 'إعراب: قرأَتِ الطالبةُ القصةَ\n\n• قرأَتِ: فعل ماضٍ مبني على الفتح، والتاء تاء التأنيث الساكنة\n• الطالبةُ: فاعل مرفوع وعلامة رفعه الضمة الظاهرة\n• القصةَ: مفعول به منصوب وعلامة نصبه الفتحة الظاهرة'
    },

    // Spelling rules
    spelling: {
        'همزة القطع': 'همزة القطع (أ، إ، ؤ، ئ) تُكتب وتُنطق دائماً.\n\nمواضعها:\n- الأسماء (ما عدا: اسم، ابن، ابنة، اثنان، اثنتان، امرؤ، امرأة)\n- الحروف: إلى، أو، إن، أن، إلا\n- الفعل الرباعي: أَرسَلَ، أكرَمَ\n- ماضي الثلاثي المهموز: أَكَلَ، أَخَذَ',
        'همزة الوصل': 'همزة الوصل (ا) تُنطق في البداية ولا تُنطق في الوصل.\n\nمواضعها:\n- أل التعريف: الكتاب، المدرسة\n- أمر الفعل الثلاثي: اكتُب، اذهَب\n- ماضي وأمر ومصدر الخماسي: انطلَقَ، انطلِقْ\n- ماضي وأمر ومصدر السداسي: استغفَرَ، استغفِرْ\n- الأسماء: اسم، ابن، ابنة، اثنان، اثنتان',
        'التاء المربوطة': 'التاء المربوطة (ة) تُنطق هاءً عند الوقف وتاءً عند الوصل.\n\nمواضعها:\n- آخر الاسم المؤنث: فاطمة، عائشة، مدرسة\n- آخر صفة المؤنث: جميلة، كبيرة\n- جمع التكسير الذي لا يأتي مفرده بتاء: قضاة، سعاة\n\nقاعدة: إذا وقفت على الكلمة ونطقتها هاء ← تاء مربوطة',
        'التاء المفتوحة': 'التاء المفتوحة (ت) تُنطق تاءً دائماً.\n\nمواضعها:\n- تاء الفاعل: كتبتُ، ذهبتَ\n- تاء التأنيث الساكنة: كتبَتْ، ذهبَتْ\n- جمع المؤنث السالم: معلمات، طالبات\n- آخر الاسم الثلاثي الساكن الوسط: بيت، وقت\n- آخر الحرف: ليت، لات',
        'الألف اللينة': 'الألف اللينة في آخر الكلمة:\n\n1. في الأفعال:\n- الثلاثي: تُكتب حسب أصلها (دعا ← يدعو → ألف قائمة | مشى ← يمشي → ألف مقصورة)\n- فوق الثلاثي: تُكتب ألف مقصورة (ى) ما لم يسبقها ياء: استدعى، ولكن: أعيا\n\n2. في الأسماء:\n- الثلاثي: حسب أصلها (عصا ← عصوان → ألف قائمة | فتى ← فتيان → ألف مقصورة)\n- فوق الثلاثي: ألف مقصورة (ى) ما لم يسبقها ياء: مستشفى، ولكن: دنيا'
    },

    // Common exercises
    exercises: {
        'إملاء': [
            'اكتب الكلمات التالية مع تشكيلها:\n\n1. مَدْرَسَة\n2. كِتَاب\n3. مُعَلِّم\n4. طَالِب\n5. قَلَم\n\nتمرين: أكمل بهمزة القطع أو الوصل:\n- _ذهب إلى المدرسة (اذهب)\n- _كل التفاحة (أكل)\n- _سمي أحمد (اسمي)\n- _لقى صديقه (ألقى)',
            'اكتب الجمل التالية وصحح الأخطاء:\n\n1. ذهبة البنت الى المدرسه ← ذهبت البنت إلى المدرسة\n2. كتبة المعلمه الدرس ← كتبت المعلمة الدرس\n3. اكل الولد التفاحه ← أكل الولد التفاحة'
        ],
        'نحو': [
            'حدد نوع كل جملة (اسمية أم فعلية):\n\n1. الشمسُ مشرقةٌ ← جملة اسمية\n2. يلعبُ الأطفالُ في الحديقةِ ← جملة فعلية\n3. المعلمُ يشرحُ الدرسَ ← جملة اسمية\n4. كتبَتِ الطالبةُ الواجبَ ← جملة فعلية\n5. الحديقةُ جميلةٌ ← جملة اسمية',
            'استخرج الفاعل والمفعول به:\n\n1. قرأَ أحمدُ الكتابَ ← الفاعل: أحمدُ ، المفعول به: الكتابَ\n2. شربَتِ البنتُ الحليبَ ← الفاعل: البنتُ ، المفعول به: الحليبَ\n3. زرعَ الفلاحُ الشجرةَ ← الفاعل: الفلاحُ ، المفعول به: الشجرةَ'
        ]
    }
};

// ===== AI Response Generator =====
function generateAIResponse(userMessage) {
    const msg = userMessage.trim();
    const msgLower = msg;

    // Check for parsing (إعراب) requests
    if (msgLower.includes('أعرب') || msgLower.includes('إعراب') || msgLower.includes('اعراب')) {
        return handleParsing(msg);
    }

    // Check for grammar questions
    for (const [topic, explanation] of Object.entries(ARABIC_KNOWLEDGE.grammar)) {
        if (msgLower.includes(topic)) {
            return explanation;
        }
    }

    // Check for specific question patterns
    if (msgLower.includes('الفرق بين')) {
        return handleDifference(msg);
    }

    if (msgLower.includes('تمرين') || msgLower.includes('تدريب') || msgLower.includes('أعطني')) {
        return handleExercise(msg);
    }

    if (msgLower.includes('معنى') || msgLower.includes('ما معنى') || msgLower.includes('تعريف')) {
        return handleMeaning(msg);
    }

    if (msgLower.includes('همزة')) {
        if (msgLower.includes('قطع')) return ARABIC_KNOWLEDGE.spelling['همزة القطع'];
        if (msgLower.includes('وصل')) return ARABIC_KNOWLEDGE.spelling['همزة الوصل'];
        return ARABIC_KNOWLEDGE.spelling['همزة القطع'] + '\n\n---\n\n' + ARABIC_KNOWLEDGE.spelling['همزة الوصل'];
    }

    if (msgLower.includes('تاء مربوطة') || msgLower.includes('تاء مفتوحة') || msgLower.includes('الفرق بين ة و ت')) {
        return ARABIC_KNOWLEDGE.spelling['التاء المربوطة'] + '\n\n---\n\n' + ARABIC_KNOWLEDGE.spelling['التاء المفتوحة'];
    }

    if (msgLower.includes('ألف لينة') || msgLower.includes('الألف اللينة') || msgLower.includes('ألف مقصورة')) {
        return ARABIC_KNOWLEDGE.spelling['الألف اللينة'];
    }

    if (msgLower.includes('جملة اسمية') || msgLower.includes('جملة فعلية') || msgLower.includes('أنواع الجمل') || msgLower.includes('أنواع الجملة')) {
        return ARABIC_KNOWLEDGE.grammar['الجملة الاسمية'] + '\n\n---\n\n' + ARABIC_KNOWLEDGE.grammar['الجملة الفعلية'];
    }

    if (msgLower.includes('ماضي') || msgLower.includes('مضارع') || msgLower.includes('أمر') || msgLower.includes('أزمنة الفعل')) {
        return ARABIC_KNOWLEDGE.grammar['الفعل الماضي'] + '\n\n---\n\n' + ARABIC_KNOWLEDGE.grammar['الفعل المضارع'] + '\n\n---\n\n' + ARABIC_KNOWLEDGE.grammar['فعل الأمر'];
    }

    if (msgLower.includes('مذكر') || msgLower.includes('مؤنث')) {
        return 'المذكر والمؤنث في اللغة العربية:\n\nالمؤنث الحقيقي: ما يدل على أنثى (أم، بنت، معلمة)\nالمؤنث المجازي: ما عُومل معاملة المؤنث (شمس، أرض، نار)\n\nعلامات التأنيث:\n1. التاء المربوطة (ة): معلمة، طبيبة\n2. ألف التأنيث المقصورة (ى): ذكرى، حبلى\n3. ألف التأنيث الممدودة (اء): صحراء، حمراء\n\nأمثلة في جمل:\n- المعلمةُ شرحَتِ الدرسَ (مؤنث)\n- المعلمُ شرحَ الدرسَ (مذكر)';
    }

    if (msgLower.includes('مفرد') || msgLower.includes('مثنى') || msgLower.includes('جمع')) {
        return 'العدد في اللغة العربية:\n\n1. المفرد: يدل على واحد (كتاب ، معلم)\n\n2. المثنى: يدل على اثنين\n- في الرفع: كتابان ، معلمان\n- في النصب والجر: كتابَيْن ، معلمَيْن\n\n3. الجمع:\nأ) جمع مذكر سالم: معلم ← معلمون/معلمين\nب) جمع مؤنث سالم: معلمة ← معلمات\nج) جمع تكسير: كتاب ← كُتُب ، رجل ← رِجال';
    }

    // Greeting responses
    if (msgLower.includes('مرحب') || msgLower.includes('سلام') || msgLower.includes('أهل') || msgLower.includes('هلا')) {
        return 'أهلاً وسهلاً بك! 😊 أنا معلمك الذكي للغة العربية. كيف يمكنني مساعدتك اليوم؟\n\nيمكنني مساعدتك في:\n• شرح قواعد النحو والصرف\n• إعراب الجمل\n• تصحيح الأخطاء الإملائية\n• شرح معاني الكلمات\n• تمارين وتدريبات\n\nما الذي تريد تعلمه؟';
    }

    if (msgLower.includes('شكر') || msgLower.includes('ممتاز') || msgLower.includes('رائع')) {
        return 'عفواً! يسعدني مساعدتك 😊\n\nهل تريد أن تسأل عن شيء آخر؟ يمكنني مساعدتك في المزيد من الدروس والتمارين!';
    }

    // Default response
    return getDefaultResponse(msg);
}

function handleParsing(msg) {
    // Check known parsing examples
    for (const [sentence, parsing] of Object.entries(ARABIC_KNOWLEDGE.parsing)) {
        if (msg.includes(sentence) || msg.replace(/[أإآاًٌٍَُِّْ]/g, '').includes(sentence.replace(/[أإآاًٌٍَُِّْ]/g, ''))) {
            return parsing;
        }
    }

    // Try to parse simple sentences
    const cleanMsg = msg.replace(/أعرب|إعراب|اعراب|:/g, '').trim();
    if (cleanMsg.length > 0) {
        return generateSimpleParsing(cleanMsg);
    }

    return 'أرسل لي جملة وسأحاول إعرابها لك! مثلاً:\n"أعرب: ذهب الولد إلى المدرسة"\n\nيمكنني إعراب الجمل البسيطة المكونة من فعل وفاعل ومفعول به.';
}

function generateSimpleParsing(sentence) {
    const words = sentence.split(/\s+/).filter(w => w.length > 0);

    if (words.length < 2) {
        return 'أحتاج إلى جملة مكونة من كلمتين على الأقل لإعرابها. حاول إرسال جملة كاملة مثل:\n"ذهب الولد إلى المدرسة"';
    }

    // Simple heuristic parsing
    let result = `إعراب: ${sentence}\n\n`;
    const prepositions = ['في', 'إلى', 'على', 'من', 'عن', 'بـ', 'لـ', 'ب', 'ل', 'مع', 'بين', 'فوق', 'تحت', 'أمام', 'خلف', 'حول'];

    // Detect if starts with verb (common Arabic verb patterns)
    const firstWord = words[0];
    const isVerb = /^[يتنأ]/.test(firstWord) || firstWord.length <= 4;

    if (isVerb && words.length >= 2) {
        result += `• ${words[0]}: فعل (يحتاج لتحديد زمنه وبنائه)\n`;
        result += `• ${words[1]}: فاعل مرفوع\n`;

        for (let i = 2; i < words.length; i++) {
            if (prepositions.includes(words[i])) {
                result += `• ${words[i]}: حرف جر\n`;
                if (i + 1 < words.length) {
                    result += `• ${words[i + 1]}: اسم مجرور بـ"${words[i]}"\n`;
                    i++;
                }
            } else {
                result += `• ${words[i]}: مفعول به منصوب (أو متمم)\n`;
            }
        }
    } else {
        result += `• ${words[0]}: مبتدأ مرفوع\n`;
        if (words.length >= 2) {
            result += `• ${words[1]}: خبر مرفوع\n`;
        }
        for (let i = 2; i < words.length; i++) {
            if (prepositions.includes(words[i])) {
                result += `• ${words[i]}: حرف جر\n`;
                if (i + 1 < words.length) {
                    result += `• ${words[i + 1]}: اسم مجرور\n`;
                    i++;
                }
            } else {
                result += `• ${words[i]}: متمم\n`;
            }
        }
    }

    result += '\n💡 ملاحظة: هذا إعراب تقريبي مبسّط. للحصول على إعراب دقيق، يُفضل مراجعة المعلم أو كتاب النحو.';
    return result;
}

function handleDifference(msg) {
    if (msg.includes('الفاعل') && msg.includes('المفعول')) {
        return 'الفرق بين الفاعل والمفعول به:\n\n' +
            '📌 الفاعل:\n- هو من قام بالفعل\n- مرفوع دائماً (بالضمة أو الألف أو الواو)\n- مثال: كتبَ الطالبُ ← الطالبُ هو الفاعل لأنه هو من كتب\n\n' +
            '📌 المفعول به:\n- هو من وقع عليه الفعل\n- منصوب دائماً (بالفتحة أو الياء أو الكسرة)\n- مثال: كتبَ الطالبُ الدرسَ ← الدرسَ هو المفعول به لأن الكتابة وقعت عليه\n\n' +
            '🔑 القاعدة: اسأل "من فعل؟" ← الفاعل | "ماذا فعل؟" ← المفعول به';
    }

    if (msg.includes('المبتدأ') && msg.includes('الخبر')) {
        return 'الفرق بين المبتدأ والخبر:\n\n' +
            '📌 المبتدأ:\n- هو الاسم الذي نتحدث عنه\n- يأتي في بداية الجملة الاسمية\n- مرفوع دائماً\n- مثال: الطالبُ مجتهدٌ ← الطالبُ هو المبتدأ\n\n' +
            '📌 الخبر:\n- هو المعلومة الجديدة عن المبتدأ\n- يُكمل معنى الجملة\n- مرفوع دائماً\n- مثال: الطالبُ مجتهدٌ ← مجتهدٌ هو الخبر\n\n' +
            '🔑 القاعدة: اسأل "مَن/ما هو؟" ← المبتدأ | "ما خبره/صفته؟" ← الخبر';
    }

    if (msg.includes('اسمية') && msg.includes('فعلية')) {
        return ARABIC_KNOWLEDGE.grammar['الجملة الاسمية'] + '\n\n---\n\n' + ARABIC_KNOWLEDGE.grammar['الجملة الفعلية'] +
            '\n\n🔑 القاعدة: انظر لأول كلمة:\n- تبدأ باسم ← جملة اسمية\n- تبدأ بفعل ← جملة فعلية';
    }

    if ((msg.includes('همزة القطع') || msg.includes('همزة الوصل')) || (msg.includes('القطع') && msg.includes('الوصل'))) {
        return ARABIC_KNOWLEDGE.spelling['همزة القطع'] + '\n\n---\n\n' + ARABIC_KNOWLEDGE.spelling['همزة الوصل'] +
            '\n\n🔑 طريقة التمييز: ضع "و" قبل الكلمة. إذا نطقت الهمزة فهي قطع، وإلا فهي وصل.';
    }

    return 'يمكنني شرح الفرق بين كثير من المفاهيم! جرّب أن تسأل عن:\n\n- الفرق بين الفاعل والمفعول به\n- الفرق بين المبتدأ والخبر\n- الفرق بين الجملة الاسمية والفعلية\n- الفرق بين همزة القطع وهمزة الوصل\n- الفرق بين التاء المربوطة والمفتوحة';
}

function handleExercise(msg) {
    if (msg.includes('إملاء') || msg.includes('املاء')) {
        const exercises = ARABIC_KNOWLEDGE.exercises['إملاء'];
        return exercises[Math.floor(Math.random() * exercises.length)];
    }

    if (msg.includes('نحو') || msg.includes('قواعد') || msg.includes('إعراب')) {
        const exercises = ARABIC_KNOWLEDGE.exercises['نحو'];
        return exercises[Math.floor(Math.random() * exercises.length)];
    }

    // Random exercise
    const allExercises = [...ARABIC_KNOWLEDGE.exercises['إملاء'], ...ARABIC_KNOWLEDGE.exercises['نحو']];
    return allExercises[Math.floor(Math.random() * allExercises.length)];
}

function handleMeaning(msg) {
    const meanings = {
        'مدرسة': 'مَدْرَسَة: مكان التعليم والتعلم، من الفعل "درسَ". جمعها: مدارس.',
        'كتاب': 'كِتَاب: مجموعة صفحات مكتوبة ومجلدة، من الفعل "كتبَ". جمعها: كُتُب.',
        'قلم': 'قَلَم: أداة تُستخدم للكتابة والرسم. جمعها: أقلام.',
        'معلم': 'مُعَلِّم: الشخص الذي يُعلّم ويُدرّس، من الفعل "علَّمَ". مؤنثه: معلمة. جمعه: معلمون.',
        'علم': 'عِلْم: المعرفة والإدراك، من الفعل "عَلِمَ". جمعها: علوم.',
        'نور': 'نُور: الضوء والإشراق، ضده الظلام. جمعه: أنوار.',
        'حياة': 'حَيَاة: العيش والوجود، من الفعل "حيِيَ". ضدها: الموت.',
        'أمل': 'أَمَل: الرجاء والتطلع للأفضل. جمعه: آمال.',
        'صبر': 'صَبْر: تحمّل الشدائد والمصاعب بهدوء. ضده: الجزع.'
    };

    for (const [word, meaning] of Object.entries(meanings)) {
        if (msg.includes(word)) {
            return meaning;
        }
    }

    return 'يمكنني شرح معاني الكلمات العربية الشائعة. جرّب أن تسأل عن معنى كلمة محددة مثل:\n"ما معنى كلمة مدرسة؟"\n"ما معنى كلمة علم؟"';
}

function getDefaultResponse(msg) {
    const responses = [
        'سؤال جيد! دعني أساعدك. يمكنني الإجابة عن أسئلة حول:\n\n📗 القواعد: الفاعل، المفعول به، المبتدأ، الخبر\n📘 الإعراب: أرسل جملة وسأعربها لك\n📙 الإملاء: همزة القطع والوصل، التاء المربوطة والمفتوحة\n📕 التمارين: اطلب تمريناً في النحو أو الإملاء\n\nجرّب أن تسأل سؤالاً محدداً!',
        'أنا هنا لمساعدتك في تعلم اللغة العربية! 😊\n\nبعض الأسئلة التي يمكنك طرحها:\n• ما الفرق بين الفاعل والمفعول به؟\n• أعرب: ذهب الولد إلى المدرسة\n• أعطني تمريناً في الإملاء\n• ما هي أنواع الجملة في العربية؟',
        'هذا سؤال مثير للاهتمام! للأسف لم أفهم سؤالك بالتحديد. هل يمكنك إعادة صياغته؟\n\nمثلاً يمكنك أن تسأل:\n• ما الفرق بين الجملة الاسمية والفعلية؟\n• كيف أفرّق بين التاء المربوطة والمفتوحة؟\n• أعرب جملة معينة'
    ];

    return responses[Math.floor(Math.random() * responses.length)];
}

// ===== Chat Functions =====
function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    addChatMessage(message, 'user');
    input.value = '';

    // Hide suggestions after first message
    document.getElementById('chatSuggestions').style.display = 'none';

    // Show typing indicator
    showTypingIndicator();

    // Simulate AI thinking time
    setTimeout(() => {
        removeTypingIndicator();
        const response = generateAIResponse(message);
        addChatMessage(response, 'bot');

        // Track chat messages
        AppState.progress.chatMessages++;
        saveProgress();
        checkAchievements();
    }, 800 + Math.random() * 1200);
}

function sendSuggestion(text) {
    document.getElementById('chatInput').value = text;
    sendMessage();
}

function handleChatKeypress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function addChatMessage(text, type) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}-message`;

    const avatar = type === 'bot' ? '&#129302;' : '&#128100;';
    const formattedText = text.replace(/\n/g, '<br>');

    msgDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <p>${formattedText}</p>
        </div>
    `;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">&#129302;</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}
