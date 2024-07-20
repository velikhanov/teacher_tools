document.getElementById("submit_button").addEventListener("click", function(event) {
    event.preventDefault();
    document.getElementById("text-container").innerHTML = "";
    toggleShow(document.querySelector(".loader"), "show");
    toggleShow(document.querySelector(".button-text"), "hide");
    textToAnalyze = document.getElementById("textToAnalyze").value;
    if (textToAnalyze.length === 0) {
        removeLoader();
        alert("Please enter a text to analyze!");
    } else {
        fetch("/analyze", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({textToAnalyze})
        }).then(response => response.text()).then(response => {
            parsed_response = JSON.parse(response);
            const textContainer = document.getElementById("text-container");
            parsed_response.analyzed_text.forEach(wordItem => {
                if (wordItem.default) {
                    const defaultSpan = document.createElement("span");
                    defaultSpan.className = "default";
                    defaultSpan.textContent = wordItem.default;
                    textContainer.appendChild(defaultSpan);
                } else {
                    const basedSpan = document.createElement("span");
                    basedSpan.className = "based";

                    wordItem.based.forEach(element => {
                        for (const [type, item] of Object.entries(element)) {
                            const itemSpan = document.createElement("span");
                            itemSpan.className = type;
                            itemSpan.textContent = item;
                            basedSpan.appendChild(itemSpan);
                        }
                    });

                    textContainer.appendChild(basedSpan);
                    if (wordItem.ending && Object.keys(wordItem.ending).length) {
                        const endingSpan = document.createElement("span");
                        endingSpan.className = "ending";
                        endingSpan.textContent = wordItem.ending || "";
                        textContainer.appendChild(endingSpan);
                    } else {
                        basedSpan.style.marginRight = "10px";
                    }
                }
            })
        }).then(() => removeLoader());;
    };
});

function toggleShow(block, action) {
    if (action === "show") {
        block.classList.remove("hide");
        block.classList.add("show");
    } else {
        block.classList.remove("show");
        block.classList.add("hide");
    }
}

function removeLoader() {
    toggleShow(document.querySelector(".loader"), "hide");
    toggleShow(document.querySelector(".button-text"), "show");
}
  