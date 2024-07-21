document.getElementById('repoForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const repoUrl = document.getElementById('repoUrl').value;
    const scanButton = document.getElementById('scanButton');
    const scanText = document.getElementById('scanText');
    const scanIcon = document.getElementById('scanIcon');
    const resultsSection = document.querySelector('.results');

    // Mostrar o ícone de varredura e alterar o texto do botão
    scanText.style.display = 'none';
    scanIcon.style.display = 'inline-block';

    fetch('/scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ repo_url: repoUrl })
    })
    .then(response => response.json())
    .then(data => {
        scanText.style.display = 'inline-block';
        scanIcon.style.display = 'none';
        
        const resultsList = document.getElementById('resultsList');
        resultsList.innerHTML = '';

        if (data.error) {
            resultsList.innerHTML = `<li class="list-group-item list-group-item-danger">${data.error}</li>`;
        } else if (data.length === 0) {
            resultsList.innerHTML = '<li class="list-group-item list-group-item-info">No credentials found.</li>';
        } else {
            data.forEach(item => {
                let credentialsClass = item.credentials ? 'credentials' : 'no-credentials';
                resultsList.innerHTML += `<li class="list-group-item">
                    <div class="file-path"><strong>File:</strong> <a href="${item.file_url}" target="_blank">${item.file_path}</a></div>
                    <div class="db-type"><strong>Database Type:</strong> ${item.db_type}</div>
                    <div class="${credentialsClass}"><strong>Credentials:</strong> ${item.credentials}</div>
                </li>`;
            });
        }
        
        resultsSection.style.display = 'block'; // Mostra os resultados
    })
    .catch(error => {
        scanText.style.display = 'inline-block';
        scanIcon.style.display = 'none';
        resultsSection.style.display = 'block'; // Mostra os resultados
        resultsList.innerHTML = `<li class="list-group-item list-group-item-danger">${error.message}</li>`;
    });
});
