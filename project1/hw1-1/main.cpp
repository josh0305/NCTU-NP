#include <bits/stdc++.h>
#include <semaphore.h>
#include <pthread.h>
#include <unistd.h>

using namespace std;


#define Taking_Break 0
#define Playing 1
#define Waiting 2
#define Leave 3

struct data{int start; int con_round; int rest_time; int tal_round;};

/* shared data */
int num;                //the total player
int timer = 0;          //recording the time
int guar;               //guaranteed number
vector<data> player;    //data of player
vector<int> mac1;
vector<int> mac2;        //id of playing machine
deque<int> order;      //recording the order waiting in line.
int tal_num;

/* for checking */
int counter = 0; //recording the round before get to guaranteed number

pthread_mutex_t mutex; //the right of use
sem_t command_p, complet, command_np, wait, ok;

void    *user(int id)
{

    int state = Taking_Break;
    int round_play = 0;
    int mac_id = 0;

    while(1)
    {

        switch(state){
        case Taking_Break:
            sem_wait(&command_np);
            if(player[id].start == timer)
            {
                round_play = 0;
                pthread_mutex_lock(&mutex);
                if(( !mac1.size() && !mac2.size()) && order.size() <= 1)
                {
                    mac1.push_back(id);
                    cout << timer << " " << id+1 << " start playing #1" << endl;
                    mac_id = 1;
                    state = Playing;
                }
                else if( !mac1.size() && !order.size())
                {
                    mac1.push_back(id);
                    cout << timer << " " << id+1 << " start playing #1" << endl;
                    mac_id = 1;
                    state = Playing;
                }
                else if(!mac2.size() && !order.size())
                {
                    mac2.push_back(id);
                    cout << timer << " " << id+1 << " start playing #2" << endl;
                    mac_id = 2;
                    state = Playing;
                }
                else
                {
                    order.push_back(id);
                    cout << timer << " " << id+1 << " wait in line" << endl;
                    state = Waiting;
                }
                pthread_mutex_unlock(&mutex);
            }
            sem_post(&complet);
            sem_wait(&wait);
            sem_post(&ok);
            break;

        case Waiting:
            sem_wait(&command_np);
            pthread_mutex_lock(&mutex);
            if(  !mac1.size() && !mac2.size())
            {
                if( order[1] == id)
                {
                    order.erase(order.begin()+1);
                    mac1.push_back(id);
                    cout << timer << " " << id+1 << " start playing #1" << endl;
                    mac_id = 1;
                    state = Playing;
                }
                else if(order.front() == id)
                {
                    order.pop_front();
                    mac1.push_back(id);
                    cout << timer << " " << id+1 << " start playing #1" << endl;
                    mac_id = 1;
                    state = Playing;
                }

            }
            else if(order.front() == id)
            {
                if(!mac1.size())
                {
                    order.pop_front();
                    mac1.push_back(id);
                    cout << timer << " " << id+1 << " start playing #1" << endl;
                    mac_id = 1;
                    state = Playing;
                }
                else if(!mac2.size())
                {
                    order.pop_front();
                    mac2.push_back(id);
                    cout << timer << " " << id+1 << " start playing #2" << endl;
                    mac_id = 2;
                    state = Playing;
                }
            }
            pthread_mutex_unlock(&mutex);
            sem_post(&complet);
            sem_wait(&wait);
            sem_post(&ok);
            break;

        case Playing:
            sem_wait(&command_p);
            counter++;
            player[id].tal_round--;
            round_play++;
            if(counter >= guar )
            {

				pthread_mutex_lock(&mutex);
				counter = 0;
                cout << timer << " " << id+1 << " finish playing YES #";
                if( mac_id == 1)
                {
                    cout << mac_id << endl;
                    mac1.clear();
                }
                else if(mac_id == 2)
                {
                    cout << mac_id << endl;
                    mac2.pop_back();
                }
				pthread_mutex_unlock(&mutex);
                mac_id = 0;
                state = Leave;

                tal_num--;
            }
            else if(player[id].tal_round <= 0)
            {

				pthread_mutex_lock(&mutex);
				counter = 0;
                cout << timer << " " << id+1 <<" finish playing YES #";
                if( mac_id == 1)
                {
                    cout << mac_id << endl;
                    mac1.clear();
                }
                else if(mac_id == 2)
                {
                    cout << mac_id << endl;
                    mac2.pop_back();
                }
				pthread_mutex_unlock(&mutex);
                mac_id = 0;
                state = Leave;

                tal_num--;
            }
            else if(round_play == player[id].con_round)
            {
				pthread_mutex_lock(&mutex);
                cout << timer << " " << id+1 <<" finish playing NO #";
                if( mac_id == 1)
                {
                    cout << mac_id << endl;
                    mac1.clear();
                }
                else if(mac_id == 2)
                {
                    cout << mac_id << endl;
                    mac2.pop_back();
                }
				pthread_mutex_unlock(&mutex);
                state = Taking_Break;
                mac_id = 0;
                player[id].start = timer + player[id].rest_time;
            }

            sem_post(&complet);
            sem_wait(&wait);
            sem_post(&ok);
            break;

        case Leave:
            sem_wait(&command_np);
            sem_post(&complet);
            usleep(1);
            sem_wait(&wait);
            sem_post(&ok);
            break;

        default:
            break;
        }
    }
}

int main(int argc, char *argv[])
{
    sem_init(&command_p, 0, 0);
    sem_init(&command_np, 0, 0);
    sem_init(&complet, 0, 0);
    sem_init(&wait, 0, 0);
    sem_init(&ok, 0, 0);

    ifstream input;
    input.open(argv[1]);
    input >> guar >> num;
    tal_num = num;


    pthread_mutex_init(&mutex, NULL);
    pthread_t tid[num];
    pthread_attr_t attr;
    pthread_attr_init(&attr);


    for(int i = 0; i < num; i++)
    {

        data doc;
        input >> doc.start >> doc.con_round >> doc.rest_time >> doc.tal_round;
        player.push_back(doc);

    }


    for(int i = 0; i < num; i++)
    {
        pthread_create(&tid[i], &attr, (void *(*)(void *))user, (void*)i);
    }

    for(timer = 0; timer <= 10000; timer++)
    {
        int i;
        if(!mac1.size() && !mac2.size())//nobody playing
        {
            counter = 0;
            i = num;
        }
        else if( !mac1.size() || !mac2.size())
        {
            i = num-1;
            sem_post(&command_p);
            sem_wait(&complet);
            sem_post(&wait);
            sem_post(&ok);
        }
        else
        {
            i = num-2;
            sem_post(&command_p);
            sem_wait(&complet);
            sem_post(&command_p);
            sem_wait(&complet);
            usleep(1);
            sem_post(&wait);
            sem_post(&wait);
            sem_wait(&ok);
            sem_wait(&ok);
        }
        for(int j = 0;j < i; j++)
        {
            sem_post(&command_np);
        }
        for(int j = 0;j < i; j++)
        {
            sem_wait(&complet);
        }
        usleep(1);
        for(int j = 0; j< i; j++)
        {
            sem_post(&wait);
        }
        for(int j = 0; j < i; j++)
        {
            sem_wait(&ok);
        }
        if(tal_num == 0)
            break;
    }


    return 0;
}
