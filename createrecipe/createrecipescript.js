// Add ingredient input fields dynamically
var addIngredientBtns = document.querySelectorAll('.addIngredientBtn');
addIngredientBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
        // Get the container for ingredients
        var ingredientsContainer = btn.previousElementSibling;

        // Create a new ingredient div
        var newIngredientDiv = document.createElement('div');
        newIngredientDiv.classList.add('ingredient');
        
        // Create input fields for ingredient name and quantity
        var nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.classList.add('ingredient-name');
        nameInput.placeholder = 'Ingredient Name';
        
        var quantityInput = document.createElement('input');
        quantityInput.type = 'text';
        quantityInput.classList.add('ingredient-quantity');
        quantityInput.placeholder = 'Quantity';
        
        // Append input fields to the new ingredient div
        newIngredientDiv.appendChild(nameInput);
        newIngredientDiv.appendChild(quantityInput);
        
        // Append the new ingredient div to the ingredients container
        ingredientsContainer.appendChild(newIngredientDiv);
    });
});
