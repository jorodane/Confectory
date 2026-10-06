/* Contract fixture only: emulates User32/GDI ABI callbacks on Linux, not Windows UX. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
int16_t GetKeyState(int32_t key){(void)key;return 0;}
uint32_t GetCurrentThreadId(void){return (uint32_t)syscall(SYS_gettid);}
typedef intptr_t (*proc_t)(intptr_t,uint32_t,intptr_t,intptr_t);
static proc_t callback;
struct window { intptr_t handle; int width,height,alive; };
static struct window windows[32];static int nwindow;static intptr_t focus;
struct message {intptr_t hwnd;uint32_t msg;uint32_t pad;intptr_t wp,lp;uint32_t time;int x,y;uint32_t private;};
static struct message queue[512];static int front,back;static int counters[24];static int64_t nextgdi=1000;
static struct window *find(intptr_t h){for(int i=0;i<nwindow;i++)if(windows[i].handle==h)return &windows[i];return 0;}
int SimCounter(int index){return counters[index];}
intptr_t SimSend(intptr_t hwnd,uint32_t msg,intptr_t wp,intptr_t lp){return callback(hwnd,msg,wp,lp);}
void SimPost(intptr_t hwnd,uint32_t msg,intptr_t wp,intptr_t lp){queue[back++%512]=(struct message){.hwnd=hwnd,.msg=msg,.wp=wp,.lp=lp};}
void SimKey(int key){SimPost(focus,0x100,key,0);SimPost(focus,0x101,key,(intptr_t)1<<30);}
uint16_t RegisterClassExW(void *cls){uint32_t *u=cls;void **p=cls;if(u[0]!=80||!p[1])return 0;callback=(proc_t)p[1];counters[0]++;return 1;}
intptr_t GetModuleHandleW(const uint16_t *name){(void)name;return 1;}
intptr_t LoadCursorW(intptr_t h,intptr_t name){(void)h;return name;}
int AdjustWindowRectEx(int *rect,uint32_t style,int menu,uint32_t ex){(void)style;(void)menu;(void)ex;rect[0]-=8;rect[1]-=31;rect[2]+=8;rect[3]+=8;return 1;}
intptr_t CreateWindowExW(uint32_t ex,const uint16_t *cls,const uint16_t *title,uint32_t style,int x,int y,int width,int height,intptr_t parent,intptr_t menu,intptr_t instance,intptr_t param){(void)ex;(void)cls;(void)title;(void)style;(void)x;(void)y;(void)parent;(void)menu;(void)instance;(void)param;intptr_t h=100+nwindow;windows[nwindow++]=(struct window){h,width-16,height-39,1};callback(h,0x81,0,0);return h;}
intptr_t DefWindowProcW(intptr_t hwnd,uint32_t msg,intptr_t wp,intptr_t lp){(void)hwnd;(void)wp;(void)lp;if(msg==0x84){counters[1]++;return 1;}if(msg==0xA1||msg==0xA3||msg==0x112)counters[2]++;return 0;}
intptr_t SetFocus(intptr_t hwnd){intptr_t old=focus;focus=hwnd;if(old&&old!=hwnd)callback(old,8,hwnd,0);return old;}
intptr_t SetCapture(intptr_t hwnd){counters[3]++;return hwnd;}
int ReleaseCapture(void){counters[4]++;return 1;}
int ScreenToClient(intptr_t hwnd,int *point){(void)hwnd;point[0]-=100;point[1]-=100;counters[5]++;return 1;}
intptr_t BeginPaint(intptr_t hwnd,void *paint){(void)hwnd;memset(paint,0,72);counters[6]++;return 500;}
int EndPaint(intptr_t hwnd,void *paint){(void)hwnd;(void)paint;counters[7]++;return 1;}
int BitBlt(intptr_t dc,int x,int y,int width,int height,intptr_t src,int sx,int sy,uint32_t raster){(void)dc;(void)x;(void)y;(void)width;(void)height;(void)src;(void)sx;(void)sy;(void)raster;counters[8]++;return 1;}
intptr_t SelectObject(intptr_t dc,intptr_t item){(void)dc;(void)item;return 77;}
int DeleteObject(intptr_t item){(void)item;counters[9]++;return 1;}
int DeleteDC(intptr_t dc){(void)dc;counters[10]++;return 1;}
int PeekMessageW(struct message *m,intptr_t hwnd,uint32_t min,uint32_t max,uint32_t remove){(void)hwnd;(void)min;(void)max;if(front==back)return 0;*m=queue[front%512];if(remove)front++;return 1;}
int TranslateMessage(void *m){(void)m;return 1;}
intptr_t DispatchMessageW(struct message *m){return callback(m->hwnd,m->msg,m->wp,m->lp);}
intptr_t GetDC(intptr_t hwnd){return hwnd+10000;}
int ReleaseDC(intptr_t hwnd,intptr_t dc){(void)hwnd;(void)dc;return 1;}
int GetClientRect(intptr_t hwnd,int *rect){struct window*w=find(hwnd);if(!w)return 0;rect[0]=rect[1]=0;rect[2]=w->width;rect[3]=w->height;return 1;}
int InvalidateRect(intptr_t hwnd,void *rect,int erase){(void)rect;if(erase)counters[11]++;for(int i=front;i<back;i++)if(queue[i%512].hwnd==hwnd&&queue[i%512].msg==15)return 1;SimPost(hwnd,15,0,0);return 1;}
intptr_t CreateCompatibleDC(intptr_t dc){(void)dc;return nextgdi++;}
intptr_t CreateCompatibleBitmap(intptr_t dc,int width,int height){(void)dc;(void)width;(void)height;counters[12]++;return nextgdi++;}
intptr_t GetStockObject(int index){return index;}
uint32_t SetDCBrushColor(intptr_t dc,uint32_t color){(void)dc;return color;}
int FillRect(intptr_t dc,void *rect,intptr_t brush){(void)dc;(void)rect;(void)brush;return 1;}
int TextOutW(intptr_t dc,int x,int y,const uint16_t *text,int count){(void)dc;(void)x;(void)y;(void)text;(void)count;return 1;}
uint32_t SetTextColor(intptr_t dc,uint32_t color){(void)dc;return color;}
int SetBkMode(intptr_t dc,int mode){(void)dc;return mode;}
int IsWindow(intptr_t hwnd){struct window*w=find(hwnd);return w&&w->alive;}
int DestroyWindow(intptr_t hwnd){struct window*w=find(hwnd);if(!w)return 0;callback(hwnd,0x82,0,0);w->alive=0;return 1;}
int UnregisterClassW(const uint16_t *name,intptr_t instance){(void)name;(void)instance;for(int i=0;i<nwindow;i++)if(windows[i].alive)return 0;counters[13]++;return 1;}

int GetTextMetricsW(intptr_t dc,void *metrics){(void)dc;memset(metrics,0,64);((int*)metrics)[0]=16;((int*)metrics)[1]=12;((int*)metrics)[2]=4;return 1;}
int GetTextExtentExPointW(intptr_t dc,const uint16_t *text,int count,int maximum,int *fit,int *advances,int *size){(void)dc;(void)maximum;int total=0;for(int i=0;i<count;i++){total+=text[i]=='W'?11:text[i]=='i'?3:text[i]>=0xAC00&&text[i]<=0xD7A3?14:7;advances[i]=total;}*fit=count;size[0]=total;size[1]=16;return 1;}
int SaveDC(intptr_t dc){(void)dc;counters[16]++;return 1;}
int RestoreDC(intptr_t dc,int saved){(void)dc;(void)saved;counters[17]++;return 1;}
int IntersectClipRect(intptr_t dc,int left,int top,int right,int bottom){(void)dc;counters[18]++;return right>left&&bottom>top?2:0;}
