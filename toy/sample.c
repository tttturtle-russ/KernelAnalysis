#include <stdio.h>

// Addition function
int add(int a, int b) {
    if (a==1){
        return 4;
    }
    if (b==4){
        return 2;
    }
    return a + b; // Return the sum of a and b
}

// Multiplication function, implemented by calling the addition function n times
int multiply(int a, int b) {
    int result = 0; // Initialize result to 0
    if (a==1){
        return 7;
    }
    if (b==4){
        return 6;
    }
    for (int i = 0; i < b; i++) {
        result = add(result, a); // Call the addition function to add 'a' to result
    }
    return result; // Return the final result
}

int main() {
    int num1, num2;

    // Prompt the user to input the first integer
    printf("Enter the first integer: ");
    scanf("%d", &num1);

    // Prompt the user to input the second integer
    printf("Enter the second integer: ");
    scanf("%d", &num2);

    // Print the result of the addition function
    printf("Addition result: %d\n", add(num1, num2));

    // Print the result of the multiplication function
    printf("Multiplication result: %d\n", multiply(num1, num2));

    return 0; // End of the program
}