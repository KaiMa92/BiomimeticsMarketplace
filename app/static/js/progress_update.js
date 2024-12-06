
        var messageCount = 0;
        document.getElementById('searchForm').onsubmit = function(event) {
            event.preventDefault();

            var userInput = document.getElementById('search').value;
            var source = new EventSource('/start?query=' + encodeURIComponent(userInput));

            source.onmessage = function(event) {
                var progressDiv = document.getElementById('progress');
                var newElement = document.createElement("div");
                newElement.innerHTML = event.data;

                // Increment the message counter
                messageCount += 1;

                // Assign class based on whether the count is odd or even
                if (messageCount % 2 === 0) {
                    newElement.classList.add('right-align');
                } else {
                    newElement.classList.add('left-align');
                }

                progressDiv.appendChild(newElement);
                console.log('Progress update:', event.data);  // Debugging
            };

            // Listen for the 'done' event
            source.addEventListener('done', function(event) {
                source.close();
                console.log('Received done event with data:', event.data); // Debugging
                var data = JSON.parse(event.data);
                var queryId = data.query_id;
                console.log('Extracted queryId:', queryId); // Debugging
                // Redirect to the results page with queryId as a URL parameter
                window.location.href = '/results?query_id=' + encodeURIComponent(queryId);
            });

            source.onerror = function(err) {
                console.error("EventSource failed:", err);
                source.close();
            };
        };
