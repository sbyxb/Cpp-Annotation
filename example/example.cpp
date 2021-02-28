#include "example.h"

// test class const func
void Example::TestClassFunc1(const ST_TEST &stTestIn, ST_TEST &stTestOut) const
{
    stTestOut = stTestIn;
    int nRet = TestClassFunc2(stTestIn.nValue, stTestOut.nValue);
    printf("TestClassFunc1\n");
}

// test class static func
int Example::TestClassFunc2(int nParam1, int &nParam2)
{
    nParam2 = nParam1;
    printf("TestClassFunc2\n");
}


