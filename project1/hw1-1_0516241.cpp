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
vector<int> use;        //id of playing machine
queue<int> order;       //recording the order waiting in line.

/* for checking */
int counter = 0; //recording the round before get to guaranteed number


pthread_mutex_t mutex; //the right of use
sem_t command_p, complet, command_np;

void    *user(int id)
{
    int state = Taking_Break;
    int round_play = 0;

    while(1)
    {
        switch(state){

        case Taking_Break:
            sem_wait(&command_np);
            if(player[id].start == timer)
            {
                round_play = 0;
                pthread_mutex_lock(&mutex);
                if(!use.size() && order.empty())
                {
                    use.push_back(id);
                    cout << timer << " " << id+1 << " start playing" << endl;
                    state = Playing;
                }
                else
                {
                    order.push(id);
                    cout << timer << " " << id+1 << " wait in line" << endl;
                    state = Waiting;
                }
                pthread_mutex_unlock(&mutex);
            }
            sem_post(&complet);
            break;

        case Waiting:
            sem_wait(&command_np);
            pthread_mutex_lock(&mutex);
            if(!use.size() && order.front() == id)
            {
                order.pop();
                use.push_back(id);
                cout << timer << " " << id+1 << " start playing" << endl;
                state = Playing;
            }
            pthread_mutex_unlock(&mutex);
            sem_post(&complet);
            break;

        case Playing:
            sem_wait(&command_p);
            counter++;
            player[id].tal_round--;
            round_play++;
            if(counter == guar)
            {
                counter = 0;
                pthread_mutex_lock(&mutex);
                use.pop_back();
                cout << timer << " " << id+1 << " finish playing YES" << endl;
                pthread_mutex_unlock(&mutex);
                state = Leave;
            }
            else if(player[id].tal_round <= 0)
            {
                counter = 0;
                pthread_mutex_lock(&mutex);
                use.pop_back();
                cout << timer << " " << id+1 <<" finish playing YES" << endl;
                pthread_mutex_unlock(&mutex);
                state = Leave;
            }
            else if(round_play == player[id].con_round)
            {
                pthread_mutex_lock(&mutex);
                use.pop_back();
                cout << timer << " " << id+1 <<" finish playing NO" << endl;
                pthread_mutex_unlock(&mutex);
                state = Taking_Break;
                player[id].start = timer + player[id].rest_time;
            }
            sem_post(&complet);
            break;

        case Leave:
            sem_wait(&command_np);
            sem_post(&complet);
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

    ifstream input;
    input.open(argv[1]);
    input >> guar >> num;


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
        if(!use.size())//nobody playing
        {
            counter = 0;
            i = num;
        }
        else
        {
            i = num-1;
            sem_post(&command_p);
            sem_wait(&complet);
        }
        for(int j = 0;j < i; j++)
        {
            sem_post(&command_np);
        }
        for(int j = 0;j < i; j++)
        {
            sem_wait(&complet);
        }

    }


    return 0;
}
