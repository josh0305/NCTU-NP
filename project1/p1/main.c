#include <stdio.h>
#include <queue>
#include <pthread.h>
#include <unistd.h>
#include <semaphore.h>

#define True 1
#define False 0

int tal_num; //the total player
int counter = 0; //recording the round before get to guaranteed number
int timer = 0; //recording the time
int guar; //guaranteed number
int use_id = 0; //the id of using the machine, and 0 is no body uses. Maybe it can be use to check if the machine is played or not.
int rest_time = 0; //the time the player should take a break
queue order; //recording the order waiting in line.
pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER; //the right of use
sem_t sem;

typedef struct data{
    int id;
    int arrive;
    int con_round;
    int rest_time;
    int tal_round;
}data;

void    *user(void *arg)
{
    data *input = (data *)arg;
    int id = input->id;
    int start = input->arrive;
    int con_round = input->con_round;
    int rest_time = input->rest_time;
    int tal_round = input->tal_round;
    int wait_in_line = False; //wait in line or not, initialize false

	int round = 0; //the total round of the guy played
	int	rest = 0; //when does the man take a break
	int status = 0; // 0 no trying 1 successfully lock 2 wait to lock

    while(tal_round > 0)
    {
        sem_wait(&sem);
        if(start >= timer)
        {
            if(use_id == 0)
            {
                use_id = id;
                printf("%d %d start playing", timer, id);
                rest_time =
            }
            else
            {
                if(wait_in_line == False)
                {
                    if(use_id != id)
                    {
                        pthread_mutex_lock(&mutex1);
                        order.push(id);
                    }
                    else
                    {
                        if(counter == guar)//лOзи
                        {
                            printf("%d %d finish playing YES")
                            use_id = order.pop();
                            printf("%d %d start playing", timer, use_id);
                            counter = 0;
                            start = 999999999999;
                        }
                        if(tal_round == 1)
                        {
                            printf("%d %d finish playing YES")
                            use_id = order.pop();
                            counter = 0;
                            start = 999999999999;
                        }
                    }
                }
            }
        }
    }

    pthread_exit(NULL);
}

int main()
{
    int num;
    pthread_t t[99999];
    scanf("%d %d", &guar, &num);
    sem_init(&sem, 0, 0);
    tal_num = num;

    int i;
    for(i = 0; i < num; i++)
    {
        data input;
        input.id = i+1;
        scanf("%d %d %d %d", &input.arrive, &input.con_round, &input.rest_time, &input.tal_round);
        pthread_create(t+i, NULL, user, (void*) &input);
        usleep(1);
    }
    for(timer = 0; timer <= num*guar; timer++)
    {
        for(i = 0; i < num; i++)
        {
            sem_post(&sem);
        }
    }

    for(i = 0; i < num; i++)
    {
        pthread_join(t[i], NULL);
    }
    return 0;
}
