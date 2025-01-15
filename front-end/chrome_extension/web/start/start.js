// googleDocsButton
document.getElementById('googleDocsButton').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'openGoogleDocs' }, (response) => {
      if (response && response.success) {
        console.log('Google Docs opened successfully');
      } else {
        console.error('Failed to open Google Docs');
      }
    });
  });
  