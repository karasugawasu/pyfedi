document.addEventListener("DOMContentLoaded", function () {
    renderMathInElement(document.querySelector('.post_body'), {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
        ],
        throwOnError: true
    });
});

document.body.addEventListener("htmx:afterSwap", function(evt) {
    // 挿入先が #preview のときだけ実行
    if (evt.target.id === "preview") {
        renderMathInElement(document.getElementById('preview'), {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false}
            ],
            throwOnError: false
        });
    }
});
