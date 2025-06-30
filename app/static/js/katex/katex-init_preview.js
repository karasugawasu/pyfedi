document.addEventListener("htmx:afterSwap", function(evt) {
    if (evt.detail.target.id === "preview") {
        renderMathInElement(document.getElementById("preview"), {
            delimiters: [
                {left: "$$", right: "$$", display: true},
                {left: "$", right: "$", display: false}
            ],
            throwOnError: false
        });
    }
});