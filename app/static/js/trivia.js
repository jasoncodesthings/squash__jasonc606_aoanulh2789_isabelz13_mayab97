// need to use dotcomloaded (wrapper waiting for html elements to load before javascript is ran)
document.addEventListener("DOMContentLoaded", function () {
        // Get trivia data cause its in jinja from html (have to use window)
        var triviaData = window.TRIVIA_DATA;
        var q = triviaData.results[0];
        // the Html sometimes decodes incorrectly returning symbols like (&*$). This decodes it safely.
        function decodeHtml(s) {
          var t = document.createElement("textarea");
          t.innerHTML = s;
          return t.value;
        }
        // Put decoded question/difficulty/category into the page
        document.getElementById("question").textContent = decodeHtml(q.question);
        document.getElementById("difficulty").textContent = decodeHtml(q.difficulty);
        document.getElementById("category").textContent = decodeHtml(q.category);
        // Collect answers: correct + incorrect, then shuffle them
        var correctRaw = q.correct_answer;
        var correctDecoded = decodeHtml(correctRaw);
        var answersRaw = q.incorrect_answers.slice();
        answersRaw.push(correctRaw);

      // Shuffling using the Knuth Shuffle  (reordering elements by iterating from the end and swapping each element with a random one)
        for (var i = answersRaw.length - 1; i > 0; i--) {
          var j = Math.floor(Math.random() * (i + 1));
          var tmp = answersRaw[i];
          answersRaw[i] = answersRaw[j];
          answersRaw[j] = tmp;
        }
        // This prevents user from submitting multiple answers
        var answered = false;
        var answersDiv = document.getElementById("answers");

        function disableAll() {
          var btns = answersDiv.querySelectorAll("button");
          btns.forEach(function(b) { b.disabled = true; });
        }
        // Creates a submit button for each answer choice
        answersRaw.forEach(function(ansRaw) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.textContent = decodeHtml(ansRaw);
          btn.className = "bg-indigo-200 px-4 py-2 rounded hover:bg-indigo-300";
          btn.onclick = function() {
            if (answered) return;
            answered = true;

            var pickedDecoded = decodeHtml(ansRaw);
            document.getElementById("selectedAnswer").value = pickedDecoded;

            if (pickedDecoded === correctDecoded) {
              document.getElementById("message").textContent = "Correct";
            } else {
              document.getElementById("message").textContent =
                "Incorrect. Correct answer: " + correctDecoded;
            }

            disableAll();
            var nextBtn = document.getElementById("nextBtn");
            nextBtn.disabled = false;
            nextBtn.classList.remove("bg-gray-500", "cursor-not-allowed");
            nextBtn.classList.add("bg-indigo-500", "hover:bg-indigo-600", "cursor-pointer");
          };
          answersDiv.appendChild(btn);
          answersDiv.appendChild(document.createTextNode(" "));
        });
});
