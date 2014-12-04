class Person {
};


/**
 * This is a description of my class
 */
class Room {
public:
    /** This is an example method */
    void add_person(Person person)
    {
        // do stuff
    }

private:
    Person* people_in_room;
};


int main()
{
    Person* p = new Person();

    return 0;
}
