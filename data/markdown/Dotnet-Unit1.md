# Page 1

C#( C-SHARP) 
• C# is type-safe object-oriented language. 
• It enables developers to build a variety of secure and robust applications that run 
on the .NET Framework. 
• The goal of the language is programmer productivity. 
• The C# language is platform-neutral and works with a range of platform 
specific compilers and frameworks, most notably the Microsoft .NET 
Framework for Windows. 
OBJECT ORIENTATION 
• C# is a rich implementation of the object-orientation paradigm, which includes 
encapsulation, inheritance, and polymorphism. 
• The features of C# from an object oriented perspective are:

# Page 2

Unified type system: 
• The fundamental building block in C# is an encapsulated unit of data and 
functions called a type. 
• C# has a unified type system, where all types ultimately share a common base 
type. 
CONT… 
• This means that all types, whether they represent business objects or are 
primitive types such as numbers, share the same basic set of functionality. 
• For example, any type can be converted to a string by calling its 
ToString method. 
Classes and interfaces: 
• In a traditional object-oriented paradigm, the only kind of type is a class. 
• In C#, there are several other kinds of types, one of which is an

# Page 3

interface. 
• An interface is like a class except it is only a definition for a type, not an 
implementation. 
CONT… 
• It’s particularly useful in scenarios where multiple inheritance is required (unlike 
languages such as C++, C# does not support multiple inheritance of classes). 
Properties, methods, and events: 
• In the pure object-oriented paradigm, all functions are methods. 
• Methods are only one kind of function member, which also includes properties 
and events. 
• Properties are function members that encapsulate a piece of an object’s state, 
such as a button’s color or a label’s text. 
• Events are function members that simplify acting on object state changes.

# Page 4

TYPE SAFETY 
• C# is primarily a type-safe language, 
• It means that types can interact only through protocols they define, 
thereby ensuring each type’s internal consistency. 
• For instance, C# prevents you from interacting with a string type as 
though it were an integer type. 
• If you assign a float type to a Boolean type, the compiler generates an 
error. 
• More specifically, C# supports static typing, meaning that the language 
enforces type safety at compile time. 
MEMORY MANAGEMENT 
• C# relies on the runtime to perform automatic memory management.

# Page 5

• The CLR has a garbage collector that executes as part of the program, 
reclaiming memory for objects that are no longer referenced. 
• This frees programmers from explicitly deallocating the memory for an 
object, eliminating the problem of incorrect pointers encountered in 
languages such as C++. 
• For performance-critical hotspots and interoperability, pointers and 
explicit memory allocation is permitted in blocks that are marked 
unsafe 
PLATFORM SUPPORT 
• C# is typically used for writing code that runs on Windows platforms. • 
Xamarin allows cross platform C# development for mobile applications 
• Microsoft’s ASP.NET Core is a cross-platform lightweight web hosting

# Page 6

framework that can run either on the .NET Framework or on .NET 
Core 
• It is an open source cross-platform runtime. 
C# AND THE CLR 
• C# is an object-oriented, component-oriented programming language. 
• C# depends on a runtime equipped with a host of features such as security, automatic 
memory management and exception handling. 
• Common Language Runtime (CLR) is the core of the Microsoft .NET Framework which 
provides these runtime features (.NET Core and Xamarin frameworks provide similar 
runtimes). 
• The CLR is language-neutral, allowing developers to build applications in multiple 
languages (e.g., C#, F#, Visual Basic .NET, and Managed C++). 
• C# is one of several managed languages that get compiled into managed code. 
• Managed code is represented in Intermediate Language or IL.

# Page 7

CONT.… 
• The CLR converts the IL into the native code of the machine, such as X86 or 
X64, usually just prior to execution. 
• This is referred to as Just-In-Time (JIT) compilation. 
• Ahead-of-time compilation is also available to improve startup time with large 
assemblies or resource. 
• The container for managed code is called an assembly or portable executable. 
• An assembly can be an executable file (.exe) or a library (.dll), and contains not 
only IL, but type information (metadata). 
• The presence of metadata allows assemblies to reference types in other 
assemblies without needing additional files. 
.NET ARCHITECTURE

# Page 9

MSIL(MICROSOFT INTERMEDIATE LANGUAGE)

# Page 10

OR CIL(COMMON IL) OR IL 
• All .NET source code is converted to an intermediate code known as MSIL 
which is interpreted by the CLR. 
• MSIL is OS and hardware independent code. 
• MSIL is converted to binary executable code(native code) at the point where the 
software is installed. 
JUST-IN-TIME(JIT) COMPILER 
• It compiles the IL code to native executable code(.exe or .dll) that is designed for specific 
machine and OS.

# Page 11

THE CLR AND .NET FRAMEWORK 
• The .NET Framework consists of the CLR plus a vast set of libraries. 
• The core libraries are sometimes collectively called the Base Class Library 
(BCL). The entire framework is called the Framework Class Library 
(FCL). 
• The .Net Framework class library (FCL) provides the core functionality of 
.Net Framework architecture. 
CONT… 
• The .Net Framework Class Library (FCL) includes a huge collection of 
reusable classes, interfaces, and value types that ease and optimize the 
development process and provide access to system functionality. 
• This library is categorized into different modules and can access to

# Page 12

Windows application, Web development, Network programming ,IO 
etc. 
COMMON TYPE SYSTEM(CTS) 
• CTS define how types are declared, used and managed in the CLR, 
• It is also an important part of the runtime's support for cross-language 
integration. 
The common type system performs the following functions: 
i. Establishes a framework that helps enable cross-language integration, type 
safety, and high-performance code execution. 
ii. Provides an object-oriented model that supports the complete 
implementation of many programming languages. 
CONT…

# Page 13

• Defines rules that languages must follow, which helps ensure that objects written 
in different languages can interact with each other. 
• Provides a library that contains the primitive data types (such as Boolean, 
Byte, Char, Int32, and UInt64) used in application development. 
COMMON LANGUAGE SPECIFICATION 
• CLS is a set of basic language features that .Net Languages needed to develop 
Applications and Services. 
• It is a subset of the CTS. The CLS establishes the minimum set of rules to 
promote language interoperability. 
• When there is a situation to communicate Objects written in different .Net 
Complaint languages. 
• Those objects must expose the features that are common to all the languages. 
• It ensures complete interoperability among applications, regardless of the

# Page 14

language used to create the application. 
CONT… 
• Microsoft has defined CLS, which are nothing but guidelines, that language should 
follow so that it can communicate with other .NET languages in a seamless 
manner. 
OTHER FRAMEWORKS 
• The Microsoft .NET Framework is the most expansive and mature framework, 
but runs only on Microsoft Windows (desktop/server). 
• Over the years, other frame‐ works have emerged to support other platforms. 
• There are currently three major players besides the .NET Framework, all of 
which are currently owned by Micro‐ soft: 
CONTD…

# Page 15

Universal Windows Platform (UWP) : 
• For writing Windows 10 Store Apps and for targeting Windows 10 devices 
(mobile, XBox, Surface Hub, Hololens). 
• The app runs in a sandbox to lessen the threat of malware, prohibiting 
operations such as reading or writing arbitrary files 
CONTD… 
.NET Core with ASP.NET Core: 
• An open source framework (originally based on a cut-down version of the .NET 
Framework) for writing easily deployable Internet apps and micro services that 
run on Windows, macOS, and Linux. 
• Unlike the .NET Frame‐ work, .NET Core can be packaged with the web 
application and xcopy deployed (self-contained deployment).

# Page 16

Xamarin : 
• For writing mobile apps that target iOS, Android, and Windows Mobile. 
The Xamarin company was purchased by Microsoft in 2016 
LEGACY AND NICHE FRAMEWORKS 
The following frameworks are still available to support older platforms: 
• Windows Runtime for Windows 8/8.1 (now UWP) 
• Windows Phone 7/8 (now UWP) 
• Microsoft XNA for game development (now UWP) 
• Silverlight (no longer actively developed since the rise of HTML5 and Java‐ 
• Script) 
• .NET Core 1.x (the predecessor to .NET Core 2.0, with significantly reduced 
functionality

# Page 17

CONTD… 
There are also a couple of niche frameworks worth mentioning: 
• The .NET Micro Framework is for running .NET code on highly resource constrained 
embedded devices (under 1 MB). 
• Mono, the open source framework upon which Xamarin sits, also has libraries to develop 
cross-platform desktop applications on Linux, macOS, and Windows. 
• Not all features are supported, or work fully. 
• It’s also possible to run managed code inside SQL Server. 
• With SQL Server CLR integration, we can write custom functions, stored procedures, 
and aggregations in C# and then call them from SQL. 
• This works in conjunction with the standard .NET Framework 
WINDOWS RUNTIME 
• C# also interoperates with Windows Runtime (WinRT) technology.

# Page 18

WinRT means two things: 
• A language-neutral object-oriented execution interface supported in Windows 8 and 
above 
• A set of libraries baked into Windows 8 and above that support the preceding interface 
CONTD… 
The term “WinRT” has historically been used to mean two more things: 
• The predecessor to UWP, i.e., the development platform for writing Store apps for 
Windows 8/8.1, sometimes called “Metro” or “Modern” 
• The defunct mobile operating system for RISC-based tablets (“Windows RT”) that 
Microsoft released in 2011 
.NET STANDARD 
• There are three main alternatives to the .NET Framework for cross-platform 
development: 
• UWP for Windows 10 devices/desktop

# Page 19

• .NET Core/ASP.NET Core for Windows, Linux, and MacOS 
• Xamarin for mobile devices (iOS, Android, and Windows 10 devices). 
• Each implementation allows .NET code to execute in different places—Linux, 
macOS, Windows, iOS, Android, and many more. 
• These frameworks along with .NET Framework 4.6.1 and later have converged 
in their core functionality. 
• All offer a base class library (BCL) with similar types and members. 
CONTD… 
• This commonality has been formalized into a standard called .NET Standard 2.0. 
• we can choose to target .NET Standard 2.0 instead of a specific framework. 
• Library is then portable, and the same assembly will run without modification on 
(modern versions of) all four frameworks. 
• .NET Standard is a formal specification of the APIs that are common across all these 
.NET implementations.

# Page 20

• .NET Standard allows libraries to build against the agreed on set of common APIs, 
ensuring they can be used in any .NET application—mobile, desktop, IoT, web, or 
anywhere you write .NET code 
CONTD… 
• .NET Standard is not a Framework; it’s merely a specification describing a 
minimum baseline of functionality (types and members) 
• Which guarantees compatibility with a certain set of frameworks. 
• The concept is similar to C# interfaces: 
• .NET Standard is like an interface that concrete types (frameworks) can 
implement 
APPLIED TECHNOLOGIES 
User-Interface APIs : 
• User-interface–based applications can be divided into two categories: thin client,

# Page 21

which amounts to a website, 
• And rich client, which is a program the end user must download and install on a 
computer or mobile device. 
• Thin client applications, .NET provides ASP.NET and ASP.NET Core. 
• Rich-client applications that target Windows 7/8/10 desktop, • 
.NET provides the WPF and Windows Forms APIs. 
• For rich-client apps that target iOS, Android, and Windows Phone 
CONTD… 
• there’s Xamarin, and for writing rich-client store apps for Windows 10 desktop and 
devices, there’s UWP 
ASP.NET 
• Applications written using ASP.NET host under Windows IIS. 
• It can be accessed from any web browser.

# Page 22

Advantages of ASP.NET over rich-client technologies: 
• There is zero deployment at the client end. 
• Clients can run a non-Windows platform. 
• Updates are easily deployed. 
• ASP.NET application runs on the server,. 
• We design our data access layer to run in the same application domain without 
limiting security or scalability. 
• In contrast, a rich client that does the same is not generally as secure or scalable. 
CONTD… 
• The solution, with the rich client, is to insert a middle tier between the client and 
database. 
• The middle tier runs on a remote application server and communicates with the rich 
clients via WCF, Web Services, or Remoting) 
• Traditional Web Forms and the newer MVC (Model-View-Controller) API. Both build on

# Page 23

the ASP.NET infrastructure. 
• Web Forms has been part of the Framework since its inception; 
• MVC was written much later in response to the success of Ruby on Rails and MonoRail. 
• It provides, in general, a better programming abstraction than Web Forms; • It also 
allows more control over the generated HTML. 
CONTD… 
• What we lose over Web Forms is a designer. This makes Web Forms still a good 
choice for web pages with predominately static content. 
• ASP.NET applications are in the System.Web.UI namespace and its subnamespaces, and 
are in the System.Web.dll assembly. 
ASP.NET CORE 
• A relatively recent addition, ASP.NET Core is similar to ASP.NET, but runs on both 
.NET Framework and .NET Core (allowing for cross-platform deployment).

# Page 24

• ASP.NET Core features a lighter-weight modular architecture, with the ability to self-host 
in a custom process, and an open source license. 
• Unlike its predecessors, ASP.NET Core is not dependent on System.Web and the 
historical baggage of Web Forms. 
• It’s particularly suitable for micro-services and deployment inside containers. 
WINDOWS FORMS 
• It is a rich-client API that’s as old as the .NET Framework. Compared to WPF, 
Windows Forms is a relatively simple technology that provides most of the features 
we need in writing a typical Windows application. 
• It also has significant relevancy in maintaining legacy applications. 
• The Windows Forms types are in the System.Windows.Forms (in 
System.Windows.Forms.dll) and System.Drawing (in System.Drawing.dll) namespaces. 
The latter also contains the GDI+ types for drawing custom controls. 
It has a number of drawbacks, though, compared to WPF:

# Page 25

• Controls are positioned and sized in pixels, making it easy to write applications that 
break on clients whose DPI settings differ from the developer’s. 
CONTD… 
• The API for drawing nonstandard controls is GDI+, which, although reasonably flexible, is 
slow in rendering large areas. 
• Controls lack true transparency. 
• Most controls are non compositional. 
• For instance, we can’t put an image control inside a tab control header. Customizing list 
views and combo boxes is time-consuming and painful. 
• Dynamic layout is difficult to get right reliably. 
WINDOWS PRESENTATION FOUNDATION (WPF) 
• WPF was introduced in Framework 3.0 for writing rich-client applications. 
Benefits of WPF over its predecessor, Windows Forms, are as

# Page 26

follows: 
• It supports sophisticated graphics, such as arbitrary transformations, 3D rendering, 
multimedia, and true transparency. Skinning is supported through styles and 
templates. 
• Its primary measurement unit is not pixel-based, so applications display correctly at any 
DPI (dots per inch) setting. 
• It has extensive and flexible layout support, which means you can localize an application 
without danger of elements overlapping. 
• Rendering uses DirectX and is fast, taking good advantage of graphics hardware 
acceleration. 
CONTD… 
• It offers reliable data binding. 
• User interfaces can be described declaratively in XAML files that can be maintained 
independently of the “code-behind” files—this helps to separate appearance from 
functionality.

# Page 27

DISTRIBUTED SYSTEM TECHNOLOGIES 
Windows Communication Foundation (WCF) 
• WCF is a sophisticated communications infrastructure introduced in Framework 3.0. 
• WCF is flexible and configurable enough to make both of its predecessors— Remoting 
and (.ASMX) Web Services—mostly redundant. 
• WCF, Remoting, and Web Services are all alike in that they implement the following basic 
model in allowing a client and server application to communicate: 
• On the server, you indicate what methods you’d like remote client applications to be 
able to call. 
• On the client, you specify or infer the signatures of the server methods you’d like to 
call. 
CONTD… 
• On both the server and the client, you choose a transport and communication 
protocol (in WCF, this is done through a binding).

# Page 28

• The client establishes a connection to the server. 
• The client calls a remote method, which executes transparently on the server 
• WCF further decouples the client and server through service contracts and data 
contracts. 
• Conceptually, the client sends an (XML or binary) message to an end‐ point on a remote 
service, rather than directly invoking a remote method. 
• WCF is highly configurable and provides extensive support for standardized SOAP based 
messaging protocols (Simple Object Access Protocol)
