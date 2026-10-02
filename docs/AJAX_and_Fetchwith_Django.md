 Research Topic
 AJAX and Fetch with Django


What the Concept Is
AJAX, short for Asynchronous JavaScript and XML, is a technique that lets a web page send and receive data from the server in the background, without reloading the whole page. Although the name mentions XML, modern implementations almost always send JSON instead. The browser API used to do this today is called Fetch, which sends an HTTP request from JavaScript and returns a Promise that resolves once the response arrives.
In a normal Django form submission, the browser sends a full page request, Django renders and returns an entirely new HTML page, and the browser replaces everything on screen , even if only one small piece of data actually changed. With Fetch, JavaScript sends a small request, often to a dedicated view that returns a JsonResponse instead of a rendered template, and only the relevant part of the page is updated using JavaScript, leaving everything else untouched.


Why It Is Useful
In this project, the job applications list page can contain many rows, each with its own filters, sort order, and pagination state already applied. Changing one application's status through a normal form submission would reload the entire page, losing scroll position and feeling slow for such a small change. Fetch solves this problem directly: the status updates instantly with no visible page reload, which is a far better experience for a frequent, small interaction like changing a status.


Where It Was Implemented
The feature built using this concept updates a job application's status directly from the applications list table, without a full page reload.

Backend, in views.py:
The update_status_ajax view differs from every other view in the project in one key way, it returns a JsonResponse, meaning structured data, instead of render(), which returns a full HTML page. The view is protected with the require_POST decorator, ensuring the status can only be changed through a POST request rather than simply by visiting a URL, and it applies the same ownership check used everywhere else in the project, confirming the application being updated actually belongs to the logged-in user before making any change.

Frontend, in application_list.html:
 A change listener is attached to each row's status dropdown. When the user selects a new status, JavaScript sends that new value to the backend using the fetch function, manually includes Django's CSRF token in the request headers since this isn't a standard form submission, and then updates the dropdown's appearance based on the response it receives ,all without the page navigating away or reloading.


Alternative Approaches
●One alternative would have been a normal HTML form for each row, submitted through POST and reloading the page afterward. This is simpler to implement, but results in a noticeably worse user experience for small, frequent changes, and would not satisfy the requirement of updating without a full page reload.
●A second alternative is building a full REST API, for example using Django REST Framework, paired with a JavaScript frontend framework such as React or Vue. This is the standard approach for large, fully decoupled applications, but represents significant additional complexity and overhead for a project of this size and scope.


Plain Fetch paired with a small, dedicated Django view was chosen here because it requires no new dependencies, keeps the amount of new JavaScript small and easy to explain, and directly demonstrates an understanding of how the browser and server communicate , which fits well within the scope and timeline of this project.


Advantages
This approach avoids a full page reload, creating a faster and smoother interaction for the user. It requires no new dependencies or libraries, relying only on the browser's built-in Fetch API. It also preserves the existing ownership and security checks used throughout the rest of the project, and the same pattern could easily be extended to other fields or other models later if needed.

 
 Disadvantages and Limitations
This approach does require more JavaScript to write and maintain compared to a standard form submission, and errors within that JavaScript are not always as visible during development as a standard Django error page would be. The current implementation shows a simple browser alert when something fails, which is functional but not a particularly polished user experience , a production application would likely use a styled inline error message instead.
CSRF token handling also has to be done manually in JavaScript, since Django's automatic CSRF handling is built around standard form submissions rather than Fetch requests. Additionally, if JavaScript is disabled in the browser, this specific interaction would not work at all. However, this project's standard Edit form still provides a working fallback for changing an application's status, so users are never fully blocked from performing this action even in that edge case.
