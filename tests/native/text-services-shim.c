/* Explicit ABI contract fixture; not a RichEdit implementation or Windows runtime. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
const uint8_t IID_ITextHost[16]={5};
const uint8_t IID_ITextServices[16]={6};
struct host {void **vtable;};
struct service {void **vtable;struct host *host;uint16_t *text;int length,anchor,caret,refs;};
static int stats[32],failure;
static struct service *latest,*held;static struct host *held_host;
void TextProofFail(int value){failure=value;}
int TextProofCounter(int index){return stats[index];}
static int query(struct service *s,const void *iid,void **out){if(failure==1||memcmp(iid,IID_ITextServices,16)){*out=0;return (int)0x80004002u;}s->refs++;*out=s;return 0;}
static uint32_t addref(struct service *s){return (uint32_t)++s->refs;}
static uint32_t release(struct service *s){if(--s->refs)return (uint32_t)s->refs;free(s->text);free(s);stats[1]++;return 0;}
static int send(struct service *s,uint32_t message,intptr_t wp,intptr_t lp,intptr_t *result){
 *result=0;
 if(!s->host&&message!=0xE&&message!=0xD&&message!=0x434)return (int)0x80004005u;
 if((failure==3||failure==7)&&message==0xC){((intptr_t(*)(struct host *))s->host->vtable[39])(s->host);return (int)0x80004005u;}
 if(failure==5&&message==8)return (int)0x80004005u;
 if(message==7)stats[4]++;else if(message==8)stats[5]++;else if(message==0x100)stats[6]++;else if(message==0x102)stats[7]++;else if(message==0x10D||message==0x10E||message==0x10F)stats[8]++;
 if(message==0x109)return 1;
 if(message==0x100&&wp==999)return (int)0x80004005u;
 if(message==0x500){int ok=((int(*)(struct host *,uint32_t,uint32_t))s->host->vtable[14])(s->host,17,25);*result=ok;}
 if(message==0x501)((void(*)(struct host *,uint32_t))s->host->vtable[15])(s->host,17);
 if(message==0x502){((void(*)(struct host *,void *,int))s->host->vtable[9])(s->host,0,1);((void(*)(struct host *,int))s->host->vtable[10])(s->host,1);}
 if(message==0x113&&wp==17)stats[9]++;
 if(message==0x503)((void(*)(struct host *,int))s->host->vtable[17])(s->host,(int)wp);
 if(message==0x20A){stats[10]++;stats[11]=(int)wp;stats[12]=(int)lp;}
 if(message==0x505){int client[4]={0};((int(*)(struct host *,int *))s->host->vtable[24])(s->host,client);((int(*)(struct host *,void *,int,int))s->host->vtable[11])(s->host,0,2,16);((int(*)(struct host *,int,int))s->host->vtable[13])(s->host,client[0]+9,client[1]+16);((int(*)(struct host *,int))s->host->vtable[12])(s->host,1);}
 if(message==0x506){((intptr_t(*)(struct host *))s->host->vtable[39])(s->host);((intptr_t(*)(struct host *))s->host->vtable[39])(s->host);}
 if(message==0x504)((void(*)(struct host *,intptr_t,int))s->host->vtable[19])(s->host,wp,1);

 if(message==0xC){const uint16_t *text=(const uint16_t *)lp;int count=0;while(text[count])count++;uint16_t *copy=calloc((size_t)count+1,2);if(!copy)return (int)0x8007000eu;memcpy(copy,text,(size_t)count*2);free(s->text);s->text=copy;s->length=count;s->anchor=s->caret=0;*result=1;}
 else if(message==0xE)*result=s->length;
 else if(message==0xD){int count=s->length;if(count>=wp)count=(int)wp-1;if(count<0)count=0;memcpy((void *)lp,s->text,(size_t)count*2);((uint16_t *)lp)[count]=0;*result=count;}
 else if(message==0x434){((int *)lp)[0]=s->anchor;((int *)lp)[1]=s->caret;}
 else if(message==0xB1){s->anchor=wp<0?0:(int)wp;s->caret=lp<0?s->length:(int)lp;}
 return 0;
}
static int draw(struct service *s,uint32_t aspect,int index,void *pv,void *target,intptr_t dc,intptr_t hic,const int *bounds,const int *world,const int *update,void *continuation,uint32_t next,int view){
 if(!s->host)return (int)0x80004005u;
 (void)pv;(void)target;(void)hic;(void)world;(void)continuation;(void)next;(void)view;
 if(aspect!=1||index!=-1||!dc||!bounds||!update)return (int)0x80070057u;
 intptr_t hostdc=((intptr_t(*)(struct host *))s->host->vtable[3])(s->host);if(hostdc!=dc)return (int)0x80004005u;
 int client[4]={0};((int(*)(struct host *,int *))s->host->vtable[24])(s->host,client);if(memcmp(client,bounds,sizeof(client)))return (int)0x80004005u;
 if(update[0]<bounds[0]||update[1]<bounds[1]||update[2]>bounds[2]||update[3]>bounds[3])return (int)0x80070057u;
 stats[2]++;return 0;
}
static int activate(struct service *s,const int *rect){if(failure==2){((void(*)(struct host *,int))s->host->vtable[17])(s->host,1);return (int)0x80004005u;}int client[4]={0};((int(*)(struct host *,int *))s->host->vtable[24])(s->host,client);return memcmp(client,rect,sizeof(client))?(int)0x80004005u:0;}
static int deactivate(struct service *s){(void)s;return failure==6?(int)0x80004005u:0;}
static int no_op(struct service *s){(void)s;return 0;}
static int properties(struct service *s,uint32_t mask,uint32_t bits){(void)s;(void)mask;(void)bits;stats[3]++;return 0;}
static void *vtable[21];
int CreateTextServices(void *outer,struct host *host,struct service **out){
 if(outer||!host)return (int)0x80070057u;
 uint32_t bits=0;((int(*)(struct host *,uint32_t,uint32_t *))host->vtable[37])(host,0xffffffffu,&bits);if((bits&1)||!(bits&2))return (int)0x80004005u;
 void *format=0;((int(*)(struct host *,void **))host->vtable[26])(host,&format);if(!format||*(int *)format!=92)return (int)0x80004005u;
 ((int(*)(struct host *,void **))host->vtable[27])(host,&format);if(!format||*(int *)format!=156)return (int)0x80004005u;
 void *queried=0;int hr=((int(*)(struct host *,const void *,void **))host->vtable[0])(host,IID_ITextHost,&queried);if(hr||queried!=host)return (int)0x80004005u;((uint32_t(*)(struct host *))host->vtable[2])(host);
 for(int i=0;i<21;i++)vtable[i]=(void *)no_op;
 vtable[0]=(void *)query;vtable[1]=(void *)addref;vtable[2]=(void *)release;vtable[3]=(void *)send;vtable[4]=(void *)draw;vtable[9]=(void *)activate;vtable[10]=(void *)deactivate;vtable[19]=(void *)properties;
 struct service *s=calloc(1,sizeof(*s));if(!s)return (int)0x8007000eu;s->vtable=vtable;s->host=host;s->refs=1;*out=s;latest=s;stats[0]++;return failure==8?(int)0x80004005u:0;
}

/* Models documented borrowed-host semantics and arbitrary references held by native/OLE clients. */
int ShutdownTextServices(struct service *s){
 stats[14]++;if(!s)return (int)0x80070057u;if(failure==4||failure==7)return (int)0x80004005u;
 if(s->host){int rect[4];((int(*)(struct host *,int *))s->host->vtable[24])(s->host,rect);stats[17]++;int timer=((int(*)(struct host *,uint32_t,uint32_t))s->host->vtable[14])(s->host,17,25);if(timer)stats[20]++;((void(*)(struct host *,int))s->host->vtable[17])(s->host,1);if(((intptr_t(*)(struct host *))s->host->vtable[39])(s->host))stats[21]++;}
 s->host=0;stats[13]++;release(s);return 0;
}
void TextProofHoldLatest(void){held=latest;addref(held);}
void TextProofHoldHost(void){held_host=latest->host;((uint32_t(*)(struct host *))held_host->vtable[1])(held_host);}
void TextProofReleaseHost(void){if(held_host){int rect[4];((int(*)(struct host *,int *))held_host->vtable[24])(held_host,rect);stats[18]++;((uint32_t(*)(struct host *))held_host->vtable[2])(held_host);held_host=0;}}
int TextProofLateReference(void){
 if(!held||held->host)return 0;
 intptr_t result=0;int read=send(held,0xE,0,0,&result);int fail=send(held,0x500,0,0,&result);return read==0&&fail<0;
}
void TextProofReleaseHeld(void){if(held){release(held);held=0;}}

void *TextProofReleaseHostCallback(void){return (void *)TextProofReleaseHost;}
