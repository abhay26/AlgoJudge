#include<iostream>
using namespace std;

int main(){
	int a, b, c;
	int t;
	cin >> t;
	for(int i=0; i<t; i++)
	{
		cin >> a >> b;
		c = a - b;
		cout << c << endl;
	}
	return 0;
}
