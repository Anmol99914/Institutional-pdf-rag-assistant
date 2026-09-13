# Page 1

Introduction to Distributed 
Systems
Unit 1

# Page 2

CHARACTERISTICS
Historical Context and Evolution
• The evolution of computer systems has undergone a dramatic transformation 
since 1945. Initially, computers were large, expensive machines costing tens of 
thousands of dollars, operating independently due to lack of connectivity. 
However, two major technological advances in the mid-1980s revolutionized 
computing:
1. Development of Powerful Microprocessors
• Evolution from 8-bit to 16-bit, 32-bit, and 64-bit CPUs
• Achieved computing power equivalent to mainframe computers at a fraction 
of the cost
• Unprecedented price/performance improvement: 10^13 gain over 50 years
• Example: From $10 million machines executing 1 instruction/second to $1000 
machines executing 1 billion instructions/second

# Page 3

2. Invention of High-Speed Computer Networks
•Local Area Networks (LANs): Connect hundreds of machines within 
buildings 
• Transfer small amounts of information in microseconds
• Data transfer rates: 100 million to 10 billion bits/second
•Wide Area Networks (WANs): Connect millions of machines globally 
• Speed range: 64 Kbps to gigabits per second

# Page 4

Definition of a Distributed System
•A distributed system is a collection of independent computers that 
appears to its users as a single coherent system.
•Autonomous Components: System consists of independent 
computers
•Single System View: Users perceive it as one unified system
•Collaboration Requirement: Autonomous components must work 
together
•Hardware Flexibility: No assumptions about computer types or 
interconnection methods

# Page 5

Important Characteristics
1. Transparency
• Differences between computers and communication methods are hidden from 
users
• Internal organization is concealed
• Users interact consistently regardless of location and time
2. Scalability
• Easy to expand or scale the system
• Direct consequence of having independent computers
• System remains continuously available
3. Fault Tolerance
• System continues operating even when some parts fail
• Users should not notice component replacement or addition
• New parts can be added seamlessly

# Page 6

Middleware Architecture
•Distributed systems are often organized using a middleware layer that 
sits between:
•Upper Layer: Users and applications
•Lower Layer: Operating systems and basic communication facilities

# Page 7

1.2 DESIGN GOALS
•Distributed systems must meet four important goals to justify their 
complexity:
1.2.1 Making Resources Accessible
•Primary Objective
•Make it easy for users and applications to access and share remote 
resources in a controlled and efficient manner.
Types of Resources
•Printers and peripherals
•Computers and storage facilities
•Data, files, and Web pages
•Networks and databases

# Page 8

Benefits of Resource Sharing
•Economic Advantages: Shared printers, supercomputers, 
high-performance storage
•Enhanced Collaboration: Internet protocols for file exchange, email, 
documents
•Virtual Organizations: Geographically dispersed teams using groupware
•Electronic Commerce: Online buying and selling capabilities
Security Challenges
•Protection against eavesdropping and intrusion
•Secure transmission of passwords and sensitive information
•User authentication and proof of identity
•Privacy protection against tracking and profiling
•Spam and unwanted communication filtering

# Page 9

1.2.2 Distribution Transparency
•Distribution transparency means hiding the fact that processes and 
resources are physically distributed across multiple computers.

# Page 10

1.2.3 Openness
•An open distributed system offers services according to standard rules 
describing syntax and semantics.
Key Components
•Protocols: Formalized rules for message format, contents, and meaning
•Interface Definition Language (IDL): Describes service interfaces
•Complete Specifications: Everything necessary for implementation
•Neutral Specifications: Don't prescribe implementation details aces

# Page 11

Benefits of Openness
•Interoperability: Different implementations can work together
•Portability: Applications can run on different systems with same 
interfaces
•Extensibility: Easy to add/replace components without affecting others
•Flexibility: Configure systems from different components
Separating Policy from Mechanism
•Mechanism: Provides basic functionality (e.g., caching facilities)
•Policy: Defines how functionality is used (e.g., what to cache, for how 
long)
•Implementation: Rich parameter sets or pluggable components with 
standard interfaces

# Page 12

1.2.4 Scalability
•Scalability is measured along three dimensions:
1. Size Scalability
•Easy addition of more users and resources
•Problem: Centralized services become bottlenecks
2. Geographic Scalability
•Users and resources can be geographically distributed
•Problem: Synchronous communication becomes inefficient over long 
distances
3. Administrative Scalability
•Easy management across multiple administrative organizations
•Problem: Different policies and security requirements

# Page 13

1.3 TYPES OF DISTRIBUTED SYSTEMS
1.3.1 Distributed Computing Systems
A. Cluster Computing Systems
Collection of similar workstations/PCs connected by high-speed LAN, 
running the same OS.
Characteristics:
•Homogeneous hardware and software
•High-speed local network connectivity
•Parallel programming execution
•Single master node controlling compute nodes

# Page 15

Functions of Master Node:
•Node allocation for parallel programs
•Batch queue management
•User interface provision
•Middleware execution
Alternative: MOSIX System
•Provides single-system image
•Dynamic and preemptive process migration
•Ultimate distribution transparency

# Page 16

B. Grid Computing Systems
Highly heterogeneous systems bringing together resources from 
different organizations for virtual organization collaboration.
Characteristics:
•High degree of heterogeneity
•Different administrative domains
•Various hardware, software, and network technologies
•Resource sharing across organizations

# Page 18

Layer Functions:
•Fabric Layer: Interfaces to local resources, resource querying and 
management
•Connectivity Layer: Communication protocols, security, authentication, 
delegation
•Resource Layer: Single resource management, access control
•Collective Layer: Multiple resource handling, discovery, allocation, 
scheduling
•Application Layer: Virtual organization applications

# Page 19

1.3.2 Distributed Information Systems
A. Transaction Processing Systems
•Transaction Definition: Operations on databases carried out as atomic 
units with ACID properties.
ACID Properties:
•Atomic: All-or-nothing execution
•Consistent: System invariants maintained
•Isolated: Concurrent transactions don't interfere
•Durable: Committed changes are permanent

# Page 20

Transaction Primitives:

# Page 21

Nested Transactions:
•Constructed from multiple sub-transactions
•Top-level transaction can fork parallel children
•Complex administration for deep nesting
•Private universe concept for each transaction level

# Page 22

B. Enterprise Application Integration (EAI)
Enable direct communication between application components independent 
of databases.
Communication Models:
•Remote Procedure Calls (RPC) 
• Local procedure call interface
• Request packaging and response handling
• Tight coupling requirement
•Remote Method Invocation (RMI) 
• Object-oriented version of RPC
• Same principles, operates on objects
•Message-Oriented Middleware (MOM) 
• Loose coupling through message passing
• Publish/subscribe systems
• Applications subscribe to message types

# Page 24

1.3.3 Distributed Pervasive Systems
Characteristics:
•Instability as default behavior
•Small, battery-powered, mobile devices
•Wireless connections
•Minimal human administrative control
•Auto-discovery and self-configuration
Requirements for Pervasive Applications:
•Embrace Contextual Changes: Continuous environment awareness
•Encourage Ad Hoc Composition: Easy application configuration
•Recognize Sharing as Default: Information access and sharing focus

# Page 25

A. Home Systems
Components:
• Personal computers
• Consumer electronics (TV, audio, video, gaming)
• Smart phones and PDAs
• Kitchen appliances, surveillance cameras, lighting controllers
Challenges:
• Complete self-configuration and management
• Universal Plug and Play (UPnP) standards
• Personal space management
• Data synchronization across devices
Architecture Evolution:
• Traditional: Distributed across multiple devices
• Modern: Single master machine with interface devices
• Personal devices: High-capacity portable storage

# Page 26

B. Electronic Health Care Systems
Monitor individual well-being and automatically contact physicians when 
needed.
Body Area Network (BAN) Organizations:
Option A: Local Hub
Option B: Continuous Connection

# Page 28

•C. Sensor Networks
Networks of small nodes with sensing devices, typically using wireless 
communication and battery power.
Database Perspective: Sensor networks as distributed databases for 
measurement and surveillance.
Processing Approaches:
•Centralized Processing:
•Distributed Processing:

# Page 30

In-Network Processing:
•Tree-based query forwarding
•Result aggregation at branch points
•Efficient resource and energy usage
TinyDB Example:
•Declarative database interface
•Tree-based routing algorithms
•Intermediate node aggregation
•Time-spanning queries for efficiency

# Page 31

Homework
•Do a case study on THE WORLD WIDE WEB.
