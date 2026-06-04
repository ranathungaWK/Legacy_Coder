import json, urllib.request, traceback

data = {"code": """#include <stdio.h>

int main() {
    int number; 
    int i;

    // 1. Ask the user for input
    printf("Enter a whole number: ");
    
    // 2. Read the user's input and store it in the 'number' variable
    scanf("%d", &number);

    printf("\n--- Multiplication Table for %d ---\n", number);

    // 3. Loop 10 times to print the table
    for(i = 1; i <= 10; i++) {
        printf("%d x %d = %d\n", number, i, number * i);
    }

    return 0;
}
""", "language": "c"}

req = urllib.request.Request("http://localhost:8000/api/v1/modernize/", data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
try:
    resp = urllib.request.urlopen(req, timeout=300)
    print('STATUS', resp.status)
    print(resp.read().decode())
except Exception as e:
    print('ERROR', e)
    traceback.print_exc()
