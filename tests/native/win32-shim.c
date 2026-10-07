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
typedef intptr_t (*subclass_proc)(intptr_t,uint32_t,intptr_t,intptr_t,uintptr_t,uintptr_t);
static struct {intptr_t window;subclass_proc proc;uintptr_t id,data;} subclasses[32];
static int subclass_cursor=-1;
intptr_t DefSubclassProc(intptr_t window,uint32_t message,intptr_t wp,intptr_t lp){for(int n=subclass_cursor;n>=0;n--)if(subclasses[n].proc&&subclasses[n].window==window){int old=subclass_cursor;subclass_cursor=n-1;intptr_t result=subclasses[n].proc(window,message,wp,lp,subclasses[n].id,subclasses[n].data);subclass_cursor=old;return result;}return callback(window,message,wp,lp);}
intptr_t TextProofDeliver(intptr_t window,uint32_t message,intptr_t wp,intptr_t lp){int old=subclass_cursor;subclass_cursor=31;intptr_t result=DefSubclassProc(window,message,wp,lp);subclass_cursor=old;return result;}
int SetWindowSubclass(intptr_t window,subclass_proc proc,uintptr_t id,uintptr_t data){for(int n=0;n<32;n++)if(!subclasses[n].proc){subclasses[n].window=window;subclasses[n].proc=proc;subclasses[n].id=id;subclasses[n].data=data;return 1;}return 0;}
int RemoveWindowSubclass(intptr_t window,subclass_proc proc,uintptr_t id){for(int n=0;n<32;n++)if(subclasses[n].window==window&&subclasses[n].proc==proc&&subclasses[n].id==id){subclasses[n].proc=0;return 1;}return 0;}
int TextProofSubclasses(void){int count=0;for(int n=0;n<32;n++)if(subclasses[n].proc)count++;return count;}
intptr_t SimSend(intptr_t hwnd,uint32_t msg,intptr_t wp,intptr_t lp){return TextProofDeliver(hwnd,msg,wp,lp);}
void SimPost(intptr_t hwnd,uint32_t msg,intptr_t wp,intptr_t lp){queue[back++%512]=(struct message){.hwnd=hwnd,.msg=msg,.wp=wp,.lp=lp};}
void SimKey(int key){SimPost(focus,0x100,key,0);SimPost(focus,0x101,key,(intptr_t)1<<30);}
uint16_t RegisterClassExW(void *cls){uint32_t *u=cls;void **p=cls;if(u[0]!=80||!p[1])return 0;callback=(proc_t)p[1];counters[0]++;return 1;}
intptr_t GetModuleHandleW(const uint16_t *name){(void)name;return 1;}
intptr_t LoadCursorW(intptr_t h,intptr_t name){(void)h;return name;}
int AdjustWindowRectEx(int *rect,uint32_t style,int menu,uint32_t ex){(void)style;(void)menu;(void)ex;rect[0]-=8;rect[1]-=31;rect[2]+=8;rect[3]+=8;return 1;}
intptr_t CreateWindowExW(uint32_t ex,const uint16_t *cls,const uint16_t *title,uint32_t style,int x,int y,int width,int height,intptr_t parent,intptr_t menu,intptr_t instance,intptr_t param){(void)ex;(void)cls;(void)title;if(style&0x02000000)counters[19]++;(void)x;(void)y;(void)parent;(void)menu;(void)instance;(void)param;intptr_t h=100+nwindow;windows[nwindow++]=(struct window){h,width-16,height-39,1};callback(h,0x81,0,0);return h;}
static int modal_stage;
int SimModalStage(void){return modal_stage;}
void SimResize(intptr_t hwnd,int width,int height){struct window *w=find(hwnd);if(w){w->width=width;w->height=height;TextProofDeliver(hwnd,5,0,(intptr_t)((uint32_t)width|((uint32_t)height<<16)));}}
void SimModalResize(intptr_t hwnd,int width,int height){modal_stage=1;TextProofDeliver(hwnd,0x231,0,0);SimResize(hwnd,width,height);TextProofDeliver(hwnd,15,0,0);TextProofDeliver(hwnd,0x232,0,0);modal_stage=0;}
intptr_t DefWindowProcW(intptr_t hwnd,uint32_t msg,intptr_t wp,intptr_t lp){(void)hwnd;(void)wp;(void)lp;if(msg==0x84){counters[1]++;return 1;}if(msg==0xA1||msg==0xA3||msg==0x112)counters[2]++;return 0;}
intptr_t SetFocus(intptr_t hwnd){intptr_t old=focus;focus=hwnd;if(old&&old!=hwnd)TextProofDeliver(old,8,hwnd,0);return old;}
int IsChild(intptr_t parent,intptr_t child){return child==parent+10000;}
static intptr_t host_capture;
intptr_t SetCapture(intptr_t hwnd){counters[3]++;intptr_t old=host_capture;host_capture=hwnd;return old;}
int ReleaseCapture(void){counters[4]++;intptr_t old=host_capture;host_capture=0;if(old)TextProofDeliver(old,0x215,0,0);return 1;}
int ScreenToClient(intptr_t hwnd,int *point){(void)hwnd;point[0]-=100;point[1]-=100;counters[5]++;return 1;}
intptr_t BeginPaint(intptr_t hwnd,void *paint){(void)hwnd;memset(paint,0,72);counters[6]++;return 500;}
int EndPaint(intptr_t hwnd,void *paint){(void)hwnd;(void)paint;counters[7]++;return 1;}
int BitBlt(intptr_t dc,int x,int y,int width,int height,intptr_t src,int sx,int sy,uint32_t raster){(void)dc;(void)x;(void)y;(void)width;(void)height;(void)src;(void)sx;(void)sy;(void)raster;counters[8]++;return 1;}
intptr_t SelectObject(intptr_t dc,intptr_t item){(void)dc;(void)item;return 77;}
int DeleteObject(intptr_t item){(void)item;counters[9]++;return 1;}
int DeleteDC(intptr_t dc){(void)dc;counters[10]++;return 1;}
int PeekMessageW(struct message *m,intptr_t hwnd,uint32_t min,uint32_t max,uint32_t remove){(void)hwnd;(void)min;(void)max;if(front==back)return 0;*m=queue[front%512];if(remove)front++;return 1;}
int TranslateMessage(void *m){(void)m;return 1;}
intptr_t DispatchMessageW(struct message *m){return TextProofDeliver(m->hwnd,m->msg,m->wp,m->lp);}
intptr_t GetDC(intptr_t hwnd){return hwnd+10000;}
int ReleaseDC(intptr_t hwnd,intptr_t dc){(void)hwnd;(void)dc;return 1;}
int GetClientRect(intptr_t hwnd,int *rect){struct window*w=find(hwnd);if(!w)return 0;rect[0]=rect[1]=0;rect[2]=w->width;rect[3]=w->height;return 1;}
int InvalidateRect(intptr_t hwnd,void *rect,int erase){(void)rect;if(erase)counters[11]++;for(int i=front;i<back;i++)if(queue[i%512].hwnd==hwnd&&queue[i%512].msg==15)return 1;SimPost(hwnd,15,0,0);return 1;}
int UpdateWindow(intptr_t hwnd){int pending=0;for(int n=front;n<back;n++)if(queue[n%512].hwnd==hwnd&&queue[n%512].msg==15){queue[n%512].msg=0;pending=1;}if(pending)TextProofDeliver(hwnd,15,0,0);return 1;}
intptr_t CreateCompatibleDC(intptr_t dc){(void)dc;return nextgdi++;}
intptr_t CreateCompatibleBitmap(intptr_t dc,int width,int height){(void)dc;(void)width;(void)height;counters[12]++;return nextgdi++;}
intptr_t GetStockObject(int index){return index+8000;}
uint32_t SetDCBrushColor(intptr_t dc,uint32_t color){(void)dc;return color;}
static int caret_fill[6];
int FillRect(intptr_t dc,void *rect,intptr_t brush){if(brush==8000){caret_fill[0]++;memcpy(caret_fill+1,rect,16);caret_fill[5]=(int)dc;}return 1;}
int TextProofCaretFill(int index){return caret_fill[index];}
int TextOutW(intptr_t dc,int x,int y,const uint16_t *text,int count){(void)dc;(void)x;(void)y;(void)text;(void)count;return 1;}
uint32_t SetTextColor(intptr_t dc,uint32_t color){(void)dc;return color;}
int SetBkMode(intptr_t dc,int mode){(void)dc;return mode;}
int IsWindow(intptr_t hwnd){struct window*w=find(hwnd);return w&&w->alive;}
int DestroyWindow(intptr_t hwnd){struct window*w=find(hwnd);if(!w)return 0;TextProofDeliver(hwnd,0x82,0,0);w->alive=0;return 1;}
int UnregisterClassW(const uint16_t *name,intptr_t instance){(void)name;(void)instance;for(int i=0;i<nwindow;i++)if(windows[i].alive)return 0;counters[13]++;return 1;}

int GetTextMetricsW(intptr_t dc,void *metrics){(void)dc;memset(metrics,0,64);((int*)metrics)[0]=16;((int*)metrics)[1]=12;((int*)metrics)[2]=4;return 1;}
int GetTextExtentExPointW(intptr_t dc,const uint16_t *text,int count,int maximum,int *fit,int *advances,int *size){(void)dc;(void)maximum;int total=0;for(int i=0;i<count;i++){total+=text[i]=='W'?11:text[i]=='i'?3:text[i]>=0xAC00&&text[i]<=0xD7A3?14:7;advances[i]=total;}*fit=count;size[0]=total;size[1]=16;return 1;}
int SaveDC(intptr_t dc){(void)dc;counters[16]++;return 1;}
int RestoreDC(intptr_t dc,int saved){(void)dc;(void)saved;counters[17]++;return 1;}
int IntersectClipRect(intptr_t dc,int left,int top,int right,int bottom){(void)dc;counters[18]++;return right>left&&bottom>top?2:0;}

/* Additional host ABI services for the separate windowless TextServices fixture. */
uint32_t GetWindowThreadProcessId(intptr_t hwnd,void *process){(void)process;return find(hwnd)?GetCurrentThreadId():0;}
uint32_t GetSysColor(int index){(void)index;return 0xffffff;}
int ClientToScreen(intptr_t hwnd,int *point){(void)hwnd;point[0]+=100;point[1]+=100;return 1;}
int GetDeviceCaps(intptr_t dc,int index){(void)dc;return index==88||index==90?96:0;}
static int ime_context_available;static int ime_stats[12];
void TextProofImeAvailable(int available){ime_context_available=available;}
intptr_t ImmGetContext(intptr_t hwnd){(void)hwnd;if(ime_context_available)ime_stats[9]++;return ime_context_available?900:0;}
int ImmReleaseContext(intptr_t hwnd,intptr_t context){(void)hwnd;if(context==900)ime_stats[2]++;return 1;}

/* Host timers/cursor ABI fixture; no elapsed-time or operating-system simulation. */
static struct {intptr_t window;uintptr_t id;} host_timers[256];
uintptr_t SetTimer(intptr_t window,uintptr_t id,uint32_t timeout,void *proc){(void)timeout;(void)proc;for(int n=0;n<256;n++)if(host_timers[n].window==window&&host_timers[n].id==id)return id;for(int n=0;n<256;n++)if(!host_timers[n].id){host_timers[n].window=window;host_timers[n].id=id;return id;}return 0;}
int KillTimer(intptr_t window,uintptr_t id){for(int n=0;n<256;n++)if(host_timers[n].window==window&&host_timers[n].id==id){host_timers[n].id=0;return 1;}return 0;}
int TextProofTimerCount(void){int count=0;for(int n=0;n<256;n++)if(host_timers[n].id)count++;return count;}
intptr_t TextProofTimer(int index){for(int n=0;n<256;n++)if(host_timers[n].id&&index--==0)return (intptr_t)host_timers[n].id;return 0;}
intptr_t GetCapture(void){return host_capture;}
static intptr_t last_cursor;
intptr_t SetCursor(intptr_t cursor){intptr_t old=last_cursor;last_cursor=cursor;return old;}
intptr_t TextProofCursor(void){return last_cursor;}

uint32_t GetCaretBlinkTime(void){return 0xffffffffu;}
int ImmSetCompositionWindow(intptr_t context,const int *form){if(context!=900||form[0]!=2)return 0;ime_stats[0]++;ime_stats[3]=form[1];ime_stats[4]=form[2];return 1;}
int ImmSetCandidateWindow(intptr_t context,const int *form){if(context!=900||form[0]!=0||form[1]!=0x80)return 0;ime_stats[1]++;for(int n=0;n<4;n++)ime_stats[5+n]=form[4+n];return 1;}
int TextProofIme(int index){return ime_stats[index];}

static int ole_count,ole_fail;
int OleInitialize(void *reserved){(void)reserved;if(ole_fail)return (int)0x80010106u;ole_count++;return ole_count>1?1:0;}
static void (*ole_callback)(void);
void TextProofOleCallback(void (*callback)(void)){ole_callback=callback;}
void OleUninitialize(void){ole_count--;if(ole_callback){void (*call)(void)=ole_callback;ole_callback=0;call();}}
int TextProofOleCount(void){return ole_count;}
void TextProofOleFail(int fail){ole_fail=fail;}
