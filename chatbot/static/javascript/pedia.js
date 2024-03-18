function search() {
    var query = document.getElementById('search-query').value;
    fetch(`/api_app/search/?query=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
        // 검색 결과 컨테이너
        const searchResults = document.getElementById('search-results');
        if (data.message) {
            searchResults.innerHTML = `<div class="search-result-item">${data.message}</div>`;
        } else {

            // 검색 결과를 담을 빈 문자열 초기화
            let resultsHtml = '';

            // 검색 결과 items 반복 처리
            data.items.forEach(item => {
                // 각 검색 결과의 제목, 링크, 설명 처리
                const title = item.title.replace(/<b>|<\/b>/g, '');  // HTML 태그 제거
                const link = item.link;
                const description = item.description;
                
                // 결과 HTML 문자열에 추가
                resultsHtml += `
                    <div class="search-result-item">
                        <h3><a href="${link}" target="_blank">${title}</a></h3>
                        <p>${description}</p>
                    </div>
                `;
            });

        // 검색 결과 컨테이너에 최종 결과 HTML 삽입
        searchResults.innerHTML = resultsHtml;
        }
    })
    .catch(error => console.error('Error:', error));
}   