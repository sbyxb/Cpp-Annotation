#pragmna once

// test func none
void TestFuncNone()
{
    if (true)
    {
        printf("true\n");
    }
    else
    {
        printf("false\n");
    }
}


// test func param
int TestFuncParam(int nParam1, char* pParam2, int &nParam3)
{
    for (int i = 0; i < 10; ++i)
    {
        printf("i\n");
    }

    return 0;
}

struct ST_TEST
{
    int     nValue;
}

class Example
{
public:
    // Example construction
    Example(/* args */)
    {

    }
    
    // Example destruction
    ~Example()
    {

    }

    // test class const func
    void TestClassFunc1(const ST_TEST &stTestIn, ST_TEST &stTestOut) const;

    // test class static func
    static int TestClassFunc2(int nParam1, int &nParam2);

private:
    /* data */
    int         m_nData;

};


