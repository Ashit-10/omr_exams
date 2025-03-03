let studentName = ''; // Assuming you get it from local storage
let timeLeft = 600; // 10 minutes (in seconds)
let questions = [];
let score = 0;
let explanationEnabled = false; // Initially disabled

// Get query parameters
const urlParams = new URLSearchParams(window.location.search);
const fileLoc = urlParams.get('file');
const examFile = urlParams.get('exam');
let questionsFile;
let answersFile;

if (examFile) {
    questionsFile = fileLoc + `_question.txt`;
    answersFile = fileLoc + `_ans_key.txt`;

} else {
    questionsFile = fileLoc + `/question.txt`;
    answersFile = fileLoc + `/answer.txt`;
}

let subjectName = urlParams.get('subject');
const shuffleQuestions = urlParams.get('shuffle') === 'true';

if (subjectName) {
    subjectName = subjectName;
}

let headName = document.getElementById('headname');
headName.textContent = subjectName;

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function loadQuestionsAndAnswers() {
    Promise.all([
        fetch(questionsFile).then(response => response.text()),
        fetch(answersFile).then(response => response.json())
    ]).then(([questionsText, answersJson]) => {
        const lines = questionsText.split('\n').filter(line => line.trim() !== '');
        let questionList = [];
        let currentQuestion = {};

        lines.forEach(line => {
            if (line.match(/^\d+\./)) { // New question
                if (currentQuestion.question) {
                    questionList.push(currentQuestion);
                }
                currentQuestion = {
                    question: line.replace(/^\d+\.\s*/, ""), // Remove question number from the text
                    options: []
                };
            } else if (line.match(/^[A-D]\)/)) { // Options
                const optionText = line.replace(/^[A-D]\)\s*/, ""); // Remove the original label (A), B), etc.)
                currentQuestion.options.push(optionText);
            }
        });

        if (currentQuestion.question) {
            questionList.push(currentQuestion);
        }

        // Combine questions with their corresponding answers
        questions = questionList.map((q, index) => {
            const correctAnswers = answersJson[index + 1]; // Correct answer(s) from the JSON file

            // Ensure correctAnswers is an array
            const correctAnswerArray = Array.isArray(correctAnswers) ? correctAnswers : [correctAnswers];

            // Create options with their original indices
            let optionsWithIndex = q.options.map((opt, i) => ({ opt, originalIndex: i }));

            // Shuffle options if shuffle=true
            if (shuffleQuestions) {
                shuffleArray(optionsWithIndex);
            }

            // Extract shuffled options
            const shuffledOptions = optionsWithIndex.map(optObj => optObj.opt);

            // Map correct answers to their new indices
            const correctIndices = correctAnswerArray.map(correctAnswer => {
                const originalIndex = correctAnswer.charCodeAt(0) - 'A'.charCodeAt(0); // Convert A, B, C, D to indices
                return optionsWithIndex.findIndex(optObj => optObj.originalIndex === originalIndex); // Get new index
            });

            const questionObject = {
                question: q.question,
                options: shuffledOptions,
                correctAnswerIndices: correctIndices // Store the updated correct indices
            };

            //add explanation if it exists in the json
            if(answersJson[index+1].explanation){
                questionObject.explanation = answersJson[index+1].explanation;
            }

            return questionObject;
        });

        // Shuffle questions if shuffle=true
        if (shuffleQuestions) {
            shuffleArray(questions);
        }

        displayQuestions();
    }).catch(error => {
        console.error("Error loading questions or answers:", error);
    });
}

function updateTimer() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    document.getElementById('timer').textContent = `Time Left: <span class="math-inline">\{minutes\}\:</span>{seconds < 10 ? '0' : ''}${seconds}`;
    if (timeLeft <= 0) {
        clearInterval(timerInterval);
        endExam();
    } else {
        timeLeft--;
    }
}

const timerInterval = setInterval(updateTimer, 1000);
updateTimer();

function handleOptionChange(questionIndex, selectedOptionIndex, selectedRadio) {
    const floatingCircle = document.getElementById('floating-circle');
    floatingCircle.style.display = 'flex';
    const correctOptionIndices = questions[questionIndex].correctAnswerIndices;
    const selectedOptionLabel = selectedRadio.parentElement;

    // Check if selected option is among the correct answers
    const isCorrect = correctOptionIndices.includes(selectedOptionIndex);

    const correctOptions = Array.from(document.querySelectorAll(`input[name="question-${questionIndex}"]`))
        .filter((_, index) => correctOptionIndices.includes(index));
    const correctOptionLabels = correctOptions.map(option => option.parentElement);

    // Disable all radio buttons for this question after selection
    document.querySelectorAll(`input[name="question-${questionIndex}"]`).forEach(radio => {
        radio.disabled = true;
    });

    if (isCorrect) {
        showNotification('Correct', 'correct');
        selectedOptionLabel.style.backgroundColor = '#5db160'; // Light green
        correctOptionLabels.forEach(label => label.style.backgroundColor = '#5db160'); // Highlight all correct options
        score++;
    } else {
        showNotification('Incorrect', 'incorrect');
        selectedOptionLabel.style.backgroundColor = '#f4a5a5'; // Light red
        correctOptionLabels.forEach(label => label.style.backgroundColor = '#5db160'); // Highlight all correct options

        if (explanationEnabled) {
            const explanationDiv = document.createElement('div');
            explanationDiv.classList.add('explanation');
            explanationDiv.textContent = questions[questionIndex].explanation || "No explanation available.";
            selectedOptionLabel.parentElement.appendChild(explanationDiv);
            explanationDiv.style.display = 'block';
        }
    }

    updateUI();
}

function displayQuestions() {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';

    questions.forEach((q, index) => {
        const questionBox = document.createElement('div');
        questionBox.classList.add('question-box');

        const questionNumber = document.createElement('div');
        questionNumber.classList.add('question-number');
        questionNumber.textContent = `Question ${index + 1}`;

        const questionText = document.createElement('div');
        questionText.classList.add('question');
        questionText.innerHTML = q.question; // Use innerHTML to render HTML tags in the question text

        const optionsList = document.createElement('ul');
        optionsList.classList.add('options');

        q.options.forEach((opt, optIndex) => {
            const optionItem = document.createElement('li');
            const label = document.createElement('label');
            const radio = document.createElement('input');

            radio.type = 'radio';
            radio.name = `question-${index}`;
            radio.value = String.fromCharCode(65 + optIndex); // A, B, C, D serially
            radio.addEventListener('change', () => handleOptionChange(index, optIndex, radio));

            label.classList.add('option-label');
            label.appendChild(radio);

            const optionLabel = document.createElement('span');
            optionLabel.textContent = `${String.fromCharCode(65 + optIndex)}) `;
            optionLabel.style.display = 'inline-block';
            optionLabel.style.marginRight = '5px'; // Adjust spacing

            const optionContent = document.createElement('span');
            optionContent.innerHTML = opt;

            label.style.display = 'flex';
            label.style.alignItems = 'flex-start'; // Aligns content to the top
            label.style.flexWrap = 'wrap'; // Ensures text and images wrap properly

            label.appendChild(optionLabel);
            label.appendChild(optionContent);

            optionItem.appendChild(label);
            optionsList.appendChild(optionItem);
        });

        questionBox.appendChild(questionNumber);
        questionBox.appendChild(questionText);
        questionBox.appendChild(options
