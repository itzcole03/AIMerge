#Requires AutoHotkey v2.0
#SingleInstance Force
SetTitleMatchMode 2

; Global variables
enabled := false
lastActiveTime := A_TickCount
debugMode := true  ; Set to true for debugging tooltips
autonomousMode := true  ; Set to true for autonomous Accept/Reject decisions
currentMode := "main"  ; Current active chat: "main" or "supervisor"

; Window identifiers for the two Copilot chats
mainChatPosition := "left"   ; Main development chat (implementer)
assistChatPosition := "right"  ; Assistant chat (supervisor)

; Integration principles that both agents should follow - based on forgecode.dev best practices
integrationPrinciples := "INTEGRATION PRINCIPLES: 1. No mock data - Use real API calls for all operations 2. No placeholders or TODOs - Complete all implementations 3. Use real database/Redis instances for testing 4. Create concrete interfaces matching the FastAPI models exactly 5. Implement proper error boundaries and comprehensive error handling 6. Favor integration tests over unit tests with mocks 7. Create regression tests for any bugs encountered 8. Only mock time-based operations or external third-party APIs if absolutely necessary"

; Supervisor prompts for the assistant chat - using file references and specific instructions
supervisorPrompts := [
    "Review the latest work from the main agent. Using the project context I provided, verify the following: 1. Does the code directly contribute to the 'IMMEDIATE TASKS' outlined in the README? 2. Is the implementation free of ANY mock data, placeholders, or 'TODO' comments? 3. Does it adhere to the specified architecture (React/Python, real APIs)? Provide a concise report with file paths and line numbers for any required changes. If it's perfect, state 'The implementation is approved.'",

    "Analyze the main agent's last output. Cross-reference it with the `gitingest` summary. Produce a diagnostic report: What was the goal? Did the agent succeed? What files were modified? Are there any deviations from the master plan? List required code changes with file paths and line numbers.",

    "Perform a quality assurance check on the main agent's submission. Based on the high-level context, does the code meet the standards for the A1Betting platform? Check for correctness, completeness, and adherence to the no-mock-data rule. Provide your feedback as a list of actionable items for the main agent."
]

; Show debug tooltip if debugMode is enabled
ShowDebugTip(message, duration := 2000) {
    global debugMode
    if (debugMode) {
        ToolTip message, 10, 50
        SetTimer () => ToolTip(), -duration
    }
}

; Toggle assistant on/off with F9
F9:: {
    global enabled
    enabled := !enabled
    ToolTip "Copilot AFK Assistant: " (enabled ? "ON" : "OFF"), 10, 10
    SetTimer () => ToolTip(), -1000
}

; Toggle autonomous mode with F8
F8:: {
    global autonomousMode
    autonomousMode := !autonomousMode
    ToolTip "Autonomous Mode: " (autonomousMode ? "ON" : "OFF"), 10, 30
    SetTimer () => ToolTip(), -1000
}

; Configuration
SetTimer MainLoop, 3000
cycleTime := 180000  ; Time between supervisor interventions (3 minutes)
supervisorIdleTime := 300000  ; Time before supervisor becomes active (5 minutes)
gitIngestFile := "gitingest_summary.txt"  ; Now using the GitIngest summary file

; === CONFIGURATION ===
; Set the target editor executable for Cursor
editorExe := "Cursor.exe"
acceptImageFile := A_ScriptDir . "\accept.png"  ; Accept button image
rejectImageFile := A_ScriptDir . "\reject.png"  ; Reject button image

; Before sending context, regenerate the summary
RegenerateGitIngestSummary() {
    scriptPath := A_ScriptDir . "\generate_gitingest_summary.py"
    if FileExist(scriptPath) {
        RunWait "C:\\Users\\bcmad\\AppData\\Local\\Programs\\Python\\Python313\\python.exe '" scriptPath "'", , "Hide"
    }
}

; Function keys for manual control
F10:: {  ; Show automation hotkeys control page
    ShowHotkeyControlPage()
}

F11:: {  ; Manual switch to main chat 
    SwitchToMainChat()
    ShowDebugTip("Manually switched to main chat")
}

F12:: {  ; Manual send of supervisor prompt
    SwitchToSupervisor()
    SendSupervisorPrompt()
    ShowDebugTip("Manually sent supervisor prompt")
}

; Manual Accept/Reject controls
F6:: {  ; Manual Accept
    ClickAcceptButton()
    ShowDebugTip("Manual Accept triggered")
}

F7:: {  ; Manual Reject
    ClickRejectButton()
    ShowDebugTip("Manual Reject triggered")
}

; Function to click Accept button
ClickAcceptButton() {
    global acceptImageFile
    CoordMode "Pixel", "Screen"
    
    if !FileExist(acceptImageFile) {
        ShowDebugTip("Accept button image not found at: " acceptImageFile)
        return false
    }
    
    if ImageSearch(&FoundX, &FoundY, 0, 0, A_ScreenWidth, A_ScreenHeight, acceptImageFile) {
        MouseMove FoundX + 40, FoundY + 15  ; Adjust as needed for your image
        Sleep 100
        Click
        ShowDebugTip("Accept button clicked")
        return true
    } else {
        ShowDebugTip("Accept button not found")
        return false
    }
}

; Function to click Reject button
ClickRejectButton() {
    global rejectImageFile
    CoordMode "Pixel", "Screen"
    
    if !FileExist(rejectImageFile) {
        ShowDebugTip("Reject button image not found at: " rejectImageFile)
        return false
    }
    
    if ImageSearch(&FoundX, &FoundY, 0, 0, A_ScreenWidth, A_ScreenHeight, rejectImageFile) {
        MouseMove FoundX + 40, FoundY + 15  ; Adjust as needed for your image
        Sleep 100
        Click
        ShowDebugTip("Reject button clicked")
        return true
    } else {
        ShowDebugTip("Reject button not found")
        return false
    }
}

; Autonomous decision logic for Accept/Reject
MakeAutonomousDecision() {
    global currentMode
    
    ; Simple heuristic: Accept if supervisor mode and recent activity, otherwise wait
    if (currentMode == "supervisor") {
        ; In supervisor mode, be more conservative - only accept if confident
        ; For now, we'll accept 70% of the time in supervisor mode
        if (Random(1, 100) <= 70) {
            return "accept"
        } else {
            return "reject"
        }
    } else {
        ; In main mode, be more accepting of agent work
        ; Accept 85% of the time in main mode
        if (Random(1, 100) <= 85) {
            return "accept"
        } else {
            return "reject"
        }
    }
}

MainLoop() {
    global enabled, lastActiveTime, supervisorPrompts, integrationPrinciples, gitIngestFile, autonomousMode, currentMode
    static buttonCheckFailed := 0  ; Counter for failed button checks
    static lastSwitchTime := A_TickCount  ; Last time we switched between chats
    static supervisorPromptIndex := 0  ; Current supervisor prompt index
    static mainChatLastResponse := ""  ; Store last response from main chat
    static contextSent := false  ; Track if we've sent the gitIngest context
    static lastDecisionTime := A_TickCount  ; Track last Accept/Reject decision
    static conversationDetected := false  ; Track if existing conversation is detected
    static initialCheck := true  ; First run check

    if !enabled
        return
        
    ; Ensure Cursor is active for consistent behavior
    if !WinExist("ahk_exe " editorExe) {
        ShowDebugTip("Cursor editor not found")
        return
    }
    
    ; Activate Cursor
    WinActivate "ahk_exe " editorExe
    Sleep 300

    ; On first run, check for existing conversation before doing anything
    if (initialCheck) {
        ShowDebugTip("🔍 Checking for existing conversation...")
        conversationDetected := CheckForExistingConversation()
        initialCheck := false
        
        if (conversationDetected) {
            ShowDebugTip("💬 Existing conversation detected - monitoring mode")
            ; Don't send context automatically if conversation is already active
            contextSent := true  ; Prevent auto-context injection
        } else {
            ShowDebugTip("📝 No active conversation - ready for context injection")
        }
        return  ; Exit early on first check to give user time to see the detection
    }

    ; Check for Accept/Reject buttons first
    CoordMode "Pixel", "Screen"
    
    ; Check for Accept button
    if FileExist(acceptImageFile) && ImageSearch(&AcceptX, &AcceptY, 0, 0, A_ScreenWidth, A_ScreenHeight, acceptImageFile) {
        if (autonomousMode && (A_TickCount - lastDecisionTime > 10000)) {  ; Wait 10 seconds between decisions
            decision := MakeAutonomousDecision()
            if (decision == "accept") {
                ClickAcceptButton()
                lastDecisionTime := A_TickCount
                lastActiveTime := A_TickCount
                return
            }
        }
        ; If not autonomous or decision was reject, just note the button is available
        ShowDebugTip("Accept button available - press F6 to accept")
        buttonCheckFailed := 0
        return
    }

    ; Check for Reject button
    if FileExist(rejectImageFile) && ImageSearch(&RejectX, &RejectY, 0, 0, A_ScreenWidth, A_ScreenHeight, rejectImageFile) {
        if (autonomousMode && (A_TickCount - lastDecisionTime > 10000)) {  ; Wait 10 seconds between decisions
            decision := MakeAutonomousDecision()
            if (decision == "reject") {
                ClickRejectButton()
                lastDecisionTime := A_TickCount
                lastActiveTime := A_TickCount
                return
            }
        }
        ; If not autonomous or decision was accept, just note the button is available
        ShowDebugTip("Reject button available - press F7 to reject")
        buttonCheckFailed := 0
        return
    }

    ; If no buttons found, increment failure counter
    buttonCheckFailed++
    ShowDebugTip("No Accept/Reject buttons found. Failed checks: " buttonCheckFailed)

    ; Only send context if explicitly requested or if no conversation was detected initially
    ; AND we've been idle for a significant time (indicating user wants to start fresh)
    if (!contextSent && !conversationDetected && FileExist(A_ScriptDir . "\" . gitIngestFile)) {
        idleTime := A_TickCount - lastActiveTime
        if (idleTime > 30000) {  ; Wait 30 seconds before auto-injecting context
            if (currentMode == "main") {
                ShowDebugTip("📤 Sending context after idle period...")
                SendGitIngestContext()
                contextSent := true
                lastActiveTime := A_TickCount
                return
            }
        } else {
            ShowDebugTip("⏳ Waiting " . Round((30000 - idleTime) / 1000) . "s before context injection...")
            return
        }
    }

    ; Calculate idle times
    idleTime := A_TickCount - lastActiveTime
    timeSinceSwitch := A_TickCount - lastSwitchTime
    
    ; Only proceed with supervisor switching if we've confirmed the buttons aren't present
    ; by checking multiple times AND we've been idle for sufficient time
    if (buttonCheckFailed >= 5 && idleTime > supervisorIdleTime) {
        ; Time to involve the supervisor or return to main agent
        if (currentMode == "main" && timeSinceSwitch > cycleTime) {
            ; Capture main chat content for context before switching
            CaptureVisibleText()
            
            ; Switch to supervisor mode and send a prompt
            SwitchToSupervisor()
            SendSupervisorPrompt()
            
            ; Update state
            currentMode := "supervisor"
            lastSwitchTime := A_TickCount
            lastActiveTime := A_TickCount
            buttonCheckFailed := 0
            
        } else if (currentMode == "supervisor" && timeSinceSwitch > cycleTime) {
            ; Capture supervisor recommendations before switching back
            CaptureVisibleText()
            
            ; Switch back to main chat
            SwitchToMainChat()
            RelaySupervisionInsights()
            
            ; Update state
            currentMode := "main"
            lastSwitchTime := A_TickCount
            lastActiveTime := A_TickCount
            buttonCheckFailed := 0
        }
    }
}

; Switch to the supervisor chat panel (right side)
SwitchToSupervisor() {
    ShowDebugTip("Switching to supervisor chat")
    
    ; Position mouse on the right panel and click to activate it
    MouseMove A_ScreenWidth * 0.75, A_ScreenHeight * 0.5
    Sleep 100
    Click
    Sleep 500
    
    ; Focus the chat input on the right panel
    Send "^+i"  ; Default shortcut for Chat: Focus Input
    Sleep 300
}

; Switch to the main chat panel (left side)
SwitchToMainChat() {
    ShowDebugTip("Switching to main chat")
    
    ; Position mouse on the left panel and click to activate it
    MouseMove A_ScreenWidth * 0.25, A_ScreenHeight * 0.5
    Sleep 100
    Click
    Sleep 500
    
    ; Focus the chat input on the left panel
    Send "^+i"  ; Default shortcut for Chat: Focus Input
    Sleep 300
}

; Send the integration principles and gitingest context to main chat
SendGitIngestContext() {
    global gitIngestFile, integrationPrinciples
    RegenerateGitIngestSummary()  ; Always refresh summary before sending
    ShowDebugTip("Sending gitIngest context to main chat")
    SwitchToMainChat()
    Sleep 300
    
    ; First, send integration principles
    Send "^a"  ; Select all
    Sleep 100
    Send "{Delete}"  ; Clear it
    Sleep 100
    
    ; Send principles first
    A_Clipboard := "Please follow these integration principles throughout development:" integrationPrinciples
    Send "^v"
    Sleep 500
    Send "{Enter}"
    Sleep 3000  ; Wait for message to be processed
    
    ; Then, send gitingest context
    Send "^+i"  ; Focus the input again
    Sleep 300
    Send "^a"  ; Select all
    Sleep 100
    Send "{Delete}"  ; Clear it
    Sleep 100
    
    ; Generate and send the gitingest summary
    fullPath := A_ScriptDir . "\" . gitIngestFile
    if FileExist(fullPath) {
        summary := GenerateGitIngestSummary(fullPath)
        A_Clipboard := "Here is a summary of the codebase. Use this for context when implementing the frontend-backend integration: `n`n" . summary
        Send "^v"
        Sleep 500
        Send "{Enter}"
        ShowDebugTip("GitIngest context summary sent to main chat")
    } else {
        ShowDebugTip("GitIngest file not found: " . fullPath)
    }
}

; Generate a concise summary from the gitingest file
GenerateGitIngestSummary(inputFile) {
    if !FileExist(inputFile) {
        Return "Error: Input file not found."
    }

    readmeContent := ""
    fileList := []
    inReadme := false
    directoryStructure := ""
    capturingTree := false

    Loop Read, inputFile
    {
        line := A_LoopReadLine

        ; Capture README
        if (inReadme) {
            if (line == "--- END FILE: README.md ---") {
                inReadme := false
            } else {
                readmeContent .= line . "`n"
            }
        } else if (line == "--- BEGIN FILE: README.md ---") {
            inReadme := true
        } 
        
        ; Capture File List
        else if (RegExMatch(line, "^--- BEGIN FILE: (.*) ---$", &match)) {
            fileList.Push(match[1])
        }

        ; Capture Directory Tree
        else if (RegExMatch(line, "^\s*Directory structure:")) {
            capturingTree := true
        }
        else if (capturingTree && RegExMatch(line, "^\s*[└├│]")) {
            directoryStructure .= line . "`n"
        }
        else if (capturingTree && Trim(line) == "") {
            ; Stop capturing after the tree block
            capturingTree := false
        }
    }

    ; Format the file list
    formattedFileList := ""
    for index, file in fileList {
        formattedFileList .= "- " . file . "`n"
    }

    ; Assemble the final summary
    summary := "--- DIRECTORY STRUCTURE ---`n"
            . directoryStructure
            . "`n--- README.md ---`n"
            . readmeContent
            . "`n--- FILE LIST ---`n"
            . formattedFileList

    Return summary
}


; Send a supervisor prompt to the right-side chat
SendSupervisorPrompt() {
    global supervisorPrompts
    static supervisorPromptIndex := 0
    
    ; Select next prompt in sequence
    supervisorPromptIndex := Mod(supervisorPromptIndex, supervisorPrompts.Length) + 1
    
    ; Clear any existing text in the input
    Send "^a"   ; Select all
    Sleep 100
    Send "{Delete}"  ; Clear it
    Sleep 100
    
    ; Send context from main chat first
    if (A_Clipboard != "") {
        mainChatContent := "I'm reviewing the frontend-backend integration work. Here's what I can see from the main agent's latest response: " . A_Clipboard
        A_Clipboard := mainChatContent
        Send "^v"
        Sleep 300
        Send "{Enter}"
        Sleep 2000
    }
    
    ; Send the supervisor prompt
    Send "^+i"  ; Focus the input again
    Sleep 300
    A_Clipboard := supervisorPrompts[supervisorPromptIndex]
    Send "^v"
    Sleep 300
    ShowDebugTip("Sending supervisor prompt " supervisorPromptIndex ": " SubStr(supervisorPrompts[supervisorPromptIndex], 1, 50) "...")
    Send "{Enter}"
}

; Capture the visible text from the current chat window
CaptureVisibleText() {
    ; Select all text in the chat panel
    Send "^a"
    Sleep 200
    
    ; Copy the text
    Send "^c"
    Sleep 200
    
    ; Cancel the selection
    Send "{Escape}"
    Sleep 100
    
    ShowDebugTip("Captured content from current chat")
}

; Relay insights from supervisor to main agent
RelaySupervisionInsights() {
    ; Focus the chat input
    Send "^+i"
    Sleep 300
    
    ; Clear any existing text
    Send "^a"
    Sleep 100
    Send "{Delete}"
    Sleep 100
    
    ; Formulate a prompt to incorporate supervisor insights
    mainPrompt := "Based on a code review of our current integration work, please address these specific issues in your next implementation steps: 1. " . A_Clipboard . " Focus on incorporating these recommendations while maintaining the integration principles we established."
    
    A_Clipboard := mainPrompt
    Send "^v"
    Sleep 300
    Send "{Enter}"
    
    ShowDebugTip("Relayed supervision insights to main chat")
}

; Show the automation hotkeys control page
ShowHotkeyControlPage() {
    ; Create a GUI window for the hotkey control page
    hotkeyGui := Gui("+Resize +MinSize300x400", "⌨️ Automation Hotkeys & Controls")
    hotkeyGui.SetFont("s12", "Segoe UI")
    
    ; Header
    hotkeyGui.SetFont("s16 Bold", "Segoe UI")
    hotkeyGui.Add("Text", "x20 y20 w360 Center", "🎮 AUTOMATION HOTKEYS")
    
    ; Content
    hotkeyGui.SetFont("s11", "Segoe UI")
    
    ; Current status
    statusText := "Current Status: " (enabled ? "✅ ENABLED" : "❌ DISABLED")
    modeText := "Autonomous Mode: " (autonomousMode ? "🤖 ON" : "👤 OFF")
    
    hotkeyGui.Add("Text", "x20 y60 w360", statusText)
    hotkeyGui.Add("Text", "x20 y80 w360", modeText)
    
    ; Separator
    hotkeyGui.Add("Text", "x20 y110 w360 0x10")  ; SS_SUNKEN line
    
    ; Hotkey descriptions
    hotkeyText := "F9 - 🚀 Automation Toggle`n   • Enables/disables the entire automation system`n   • Works globally from any application`n   • Shows status tooltip when pressed`n`nF8 - 🤖 Autonomous Mode Toggle`n   • Switches between manual and autonomous operation`n   • When ON: AI makes accept/reject decisions automatically`n   • When OFF: You control accept/reject manually`n`nF6 - ✅ Manual Accept`n   • Manually accepts current Copilot suggestion`n   • Only works when automation is enabled`n   • Useful for overriding autonomous decisions`n`nF7 - ❌ Manual Reject`n   • Manually rejects current Copilot suggestion`n   • Only works when automation is enabled`n   • Useful for overriding autonomous decisions`n`nF5 - 🧠 Capture Current Context`n   • Captures conversation history from both windows`n   • Analyzes current development state and progress`n   • Generates contextual continuation prompts`n`nCtrl+F5 - 📤 Manual Context Injection`n   • Manually injects GitIngest context into conversation`n   • Overrides automatic conversation detection`n   • Useful for adding project context to existing chats`n`nF10 - 📖 Show This Help (Current)`n   • Displays this hotkey reference window`n   • Available anytime automation script is running`n   • Press again to refresh status`n`nF11 - 🔄 Switch to Main Chat`n   • Focuses the left Cursor window (main development)`n   • Used for primary coding and implementation`n`nF12 - 👥 Send Supervisor Prompt`n   • Switches to supervisor chat and sends review prompt`n   • Used for code review and quality assurance"
    
    hotkeyGui.Add("Text", "x20 y130 w360 r22", hotkeyText)
    
    ; Tips section
    hotkeyGui.SetFont("s10 Bold", "Segoe UI")
    hotkeyGui.Add("Text", "x20 y470 w360", "💡 USAGE TIPS:")
    
    hotkeyGui.SetFont("s10", "Segoe UI")
    tipText := "• All hotkeys work globally (any app can be focused)`n• Start with F9 to enable automation`n• Use F8 for hands-free operation`n• F6/F7 for manual control when needed`n• F5 to capture context when resuming work`n• AutoHotkey icon appears in system tray when running"
    
    hotkeyGui.Add("Text", "x20 y490 w360 r6", tipText)
    
    ; Close button
    closeBtn := hotkeyGui.Add("Button", "x150 y570 w100 h30", "✅ Got It!")
    closeBtn.OnEvent("Click", (*) => hotkeyGui.Close())
    
    ; Show the GUI
    hotkeyGui.Show("w400 h620")
    
    ; Auto-close after 30 seconds
    SetTimer(() => hotkeyGui.Close(), -30000)
    
    ShowDebugTip("Hotkey control page opened (F10)")
}

; F5 - Capture and analyze current conversation context from both windows
F5:: {
    CaptureAndAnalyzeContext()
}

; Ctrl+F5 - Manually inject GitIngest context (override conversation detection)
^F5:: {
    ManualContextInjection()
}

; Manual context injection function
ManualContextInjection() {
    global gitIngestFile, contextSent
    
    ShowDebugTip("📤 Manual context injection requested...")
    
    if !FileExist(A_ScriptDir . "\" . gitIngestFile) {
        ShowDebugTip("❌ GitIngest file not found: " . gitIngestFile)
        return
    }
    
    ; Ask user for confirmation
    result := MsgBox("Inject GitIngest context into the current conversation?`n`nThis will send project context and integration principles to the main chat.", "Manual Context Injection", "YesNo")
    
    if (result == "Yes") {
        ; Force context injection regardless of conversation detection
        contextSent := false  ; Reset flag to allow injection
        SendGitIngestContext()
        contextSent := true
        ShowDebugTip("✅ Context manually injected")
    } else {
        ShowDebugTip("❌ Context injection cancelled")
    }
}

; Comprehensive context capture and analysis system
CaptureAndAnalyzeContext() {
    ShowDebugTip("🧠 Capturing conversation context from both windows...")
    
    ; Step 1: Capture context from left window (main development chat)
    leftContext := CaptureWindowContext("left")
    Sleep 1000
    
    ; Step 2: Capture context from right window (supervisor/review chat)  
    rightContext := CaptureWindowContext("right")
    Sleep 1000
    
    ; Step 3: Analyze the captured context and generate continuation strategy
    analysisResult := AnalyzeConversationContext(leftContext, rightContext)
    
    ; Step 4: Save context to files for reference
    SaveContextToFiles(leftContext, rightContext, analysisResult)
    
    ; Step 5: Generate and send contextual continuation prompt
    GenerateContextualContinuation(analysisResult)
    
    ShowDebugTip("✅ Context analysis complete - ready for intelligent continuation")
}

; Capture conversation context from a specific window (left or right)
CaptureWindowContext(windowSide) {
    ShowDebugTip("📋 Capturing " . windowSide . " window context...")
    
    ; Focus the appropriate window
    if (windowSide == "left") {
        ; Focus left window (main development)
        MouseMove A_ScreenWidth * 0.25, A_ScreenHeight * 0.5
        Click
        Sleep 500
    } else {
        ; Focus right window (supervisor/review)
        MouseMove A_ScreenWidth * 0.75, A_ScreenHeight * 0.5
        Click
        Sleep 500
    }
    
    ; Scroll to top of conversation to capture full context
    Send "^{Home}"
    Sleep 500
    
    ; Select all conversation content
    Send "^a"
    Sleep 300
    
    ; Copy the content
    Send "^c"
    Sleep 500
    
    ; Store the captured content
    capturedContent := A_Clipboard
    
    ; Clear selection
    Send "{Escape}"
    Sleep 200
    
    ; Return to chat input area
    Send "^+i"
    Sleep 300
    
    ShowDebugTip("✅ Captured " . StrLen(capturedContent) . " characters from " . windowSide . " window")
    return capturedContent
}

; Analyze captured conversation context to understand current state
AnalyzeConversationContext(leftContext, rightContext) {
    ShowDebugTip("🔍 Analyzing conversation context...")
    
    ; Extract key information from conversations
    analysis := Map()
    
    ; Analyze left window (main development chat)
    analysis["leftSummary"] := ExtractConversationSummary(leftContext, "development")
    analysis["currentTask"] := ExtractCurrentTask(leftContext)
    analysis["lastUserRequest"] := ExtractLastUserRequest(leftContext)
    analysis["codeProgress"] := ExtractCodeProgress(leftContext)
    analysis["pendingActions"] := ExtractPendingActions(leftContext)
    
    ; Analyze right window (supervisor/review chat)  
    analysis["rightSummary"] := ExtractConversationSummary(rightContext, "review")
    analysis["reviewFeedback"] := ExtractReviewFeedback(rightContext)
    analysis["qualityIssues"] := ExtractQualityIssues(rightContext)
    analysis["approvalStatus"] := ExtractApprovalStatus(rightContext)
    
    ; Determine next best action
    analysis["recommendedAction"] := DetermineNextAction(analysis)
    analysis["continuationPrompt"] := GenerateContinuationPrompt(analysis)
    
    return analysis
}

; Extract conversation summary from context
ExtractConversationSummary(context, type) {
    ; Look for key patterns in the conversation
    summary := ""
    
    if (InStr(context, "PHENOMENAL SUCCESS")) {
        summary .= "✅ Recent success reported. "
    }
    if (InStr(context, "Performance Validation Complete")) {
        summary .= "✅ Performance validation completed. "
    }
    if (InStr(context, "integration test")) {
        summary .= "🔧 Integration testing in progress. "
    }
    if (InStr(context, "Phase 4")) {
        summary .= "📊 Working on Phase 4 implementation. "
    }
    if (InStr(context, "API endpoints")) {
        summary .= "🔌 API endpoint development focus. "
    }
    if (InStr(context, "real metrics")) {
        summary .= "📈 Real metrics implementation. "
    }
    
    return summary != "" ? summary : "General " . type . " conversation in progress."
}

; Extract the current task from conversation
ExtractCurrentTask(context) {
    ; Look for task indicators
    if (InStr(context, "integration test")) {
        return "Creating integration tests for API endpoints"
    }
    if (InStr(context, "real metrics")) {
        return "Implementing real metrics system"
    }
    if (InStr(context, "Phase 4")) {
        return "Phase 4 implementation and metrics"
    }
    if (InStr(context, "API")) {
        return "API development and integration"
    }
    
    return "Continuing current development work"
}

; Extract last user request from conversation
ExtractLastUserRequest(context) {
    ; This would need more sophisticated parsing in a real implementation
    ; For now, return a general continuation
    return "Continue with the current development task"
}

; Extract code progress indicators
ExtractCodeProgress(context) {
    progress := ""
    
    if (InStr(context, "100/100 (100.0%)")) {
        progress .= "✅ Tests passing at 100%. "
    }
    if (InStr(context, "50x faster")) {
        progress .= "⚡ Performance optimized (50x faster). "
    }
    if (InStr(context, "125x faster")) {
        progress .= "⚡ Exceptional performance gains (125x faster). "
    }
    if (InStr(context, "6x more efficient")) {
        progress .= "💾 Memory efficiency improved (6x). "
    }
    
    return progress != "" ? progress : "Development in progress."
}

; Extract pending actions from conversation
ExtractPendingActions(context) {
    actions := ""
    
    if (InStr(context, "Now let's create")) {
        actions .= "🔨 Ready to implement next feature. "
    }
    if (InStr(context, "integration test")) {
        actions .= "🧪 Integration test creation pending. "
    }
    if (InStr(context, "verify the API endpoints")) {
        actions .= "✅ API endpoint verification needed. "
    }
    
    return actions != "" ? actions : "Continue current development workflow."
}

; Extract review feedback from supervisor chat
ExtractReviewFeedback(context) {
    if (InStr(context, "Exceptional")) {
        return "✅ Exceptional work quality noted by supervisor"
    }
    if (InStr(context, "production-ready")) {
        return "✅ Code deemed production-ready"
    }
    if (InStr(context, "TDD methodology")) {
        return "✅ TDD methodology praised"
    }
    
    return "Review feedback available"
}

; Extract quality issues from supervisor chat
ExtractQualityIssues(context) {
    ; Look for criticism or issues
    if (InStr(context, "issue") || InStr(context, "problem") || InStr(context, "fix")) {
        return "⚠️ Quality issues identified requiring attention"
    }
    
    return "✅ No major quality issues identified"
}

; Extract approval status from supervisor chat
ExtractApprovalStatus(context) {
    if (InStr(context, "approved") || InStr(context, "excellent")) {
        return "✅ Work approved by supervisor"
    }
    
    return "⏳ Awaiting supervisor approval"
}

; Determine the next best action based on analysis
DetermineNextAction(analysis) {
    ; Priority logic for determining next action
    
    if (InStr(analysis["pendingActions"], "integration test")) {
        return "CREATE_INTEGRATION_TEST"
    }
    if (InStr(analysis["pendingActions"], "API endpoint")) {
        return "VERIFY_API_ENDPOINTS"
    }
    if (InStr(analysis["currentTask"], "Phase 4")) {
        return "CONTINUE_PHASE4"
    }
    if (InStr(analysis["qualityIssues"], "issues identified")) {
        return "ADDRESS_QUALITY_ISSUES"
    }
    
    return "CONTINUE_DEVELOPMENT"
}

; Generate contextual continuation prompt
GenerateContinuationPrompt(analysis) {
    basePrompt := "I'm resuming our development session. Based on the conversation history, I can see that:\n\n"
    
    ; Add context summary
    basePrompt .= "📊 CURRENT STATE:\n"
    basePrompt .= "• Main Chat: " . analysis["leftSummary"] . "\n"
    basePrompt .= "• Review Chat: " . analysis["rightSummary"] . "\n"
    basePrompt .= "• Current Task: " . analysis["currentTask"] . "\n"
    basePrompt .= "• Code Progress: " . analysis["codeProgress"] . "\n\n"
    
    ; Add specific continuation based on recommended action
    switch analysis["recommendedAction"] {
        case "CREATE_INTEGRATION_TEST":
            basePrompt .= "🧪 NEXT ACTION: I'll create the integration test to verify API endpoints work with real metrics as discussed.\n\n"
        case "VERIFY_API_ENDPOINTS":
            basePrompt .= "🔌 NEXT ACTION: I'll verify the API endpoints are working correctly with the new metrics system.\n\n"
        case "CONTINUE_PHASE4":
            basePrompt .= "📈 NEXT ACTION: I'll continue with Phase 4 implementation focusing on the metrics system.\n\n"
        case "ADDRESS_QUALITY_ISSUES":
            basePrompt .= "🔧 NEXT ACTION: I'll address the quality issues identified in the review.\n\n"
        default:
            basePrompt .= "🚀 NEXT ACTION: I'll continue with the current development workflow.\n\n"
    }
    
    basePrompt .= "Please confirm if this continuation aligns with your expectations, or let me know if you'd like me to focus on a different aspect."
    
    return basePrompt
}

; Save captured context to files for reference
SaveContextToFiles(leftContext, rightContext, analysis) {
    ; Save to timestamped files
    timestamp := FormatTime(, "yyyy-MM-dd_HH-mm-ss")
    
    ; Save left context
    leftFile := A_ScriptDir . "\context_main_" . timestamp . ".txt"
    FileAppend leftContext, leftFile
    
    ; Save right context  
    rightFile := A_ScriptDir . "\context_review_" . timestamp . ".txt"
    FileAppend rightContext, rightFile
    
    ; Save analysis summary
    analysisFile := A_ScriptDir . "\context_analysis_" . timestamp . ".txt"
    analysisContent := "CONTEXT ANALYSIS - " . timestamp . "`n"
    analysisContent .= "=" . StrReplace(StrLen("CONTEXT ANALYSIS - " . timestamp), ".", "=") . "`n`n"
    
    for key, value in analysis {
        analysisContent .= key . ": " . value . "`n"
    }
    
    FileAppend analysisContent, analysisFile
    
    ShowDebugTip("💾 Context saved to files with timestamp: " . timestamp)
}

; Generate and send contextual continuation to main chat
GenerateContextualContinuation(analysis) {
    ShowDebugTip("🚀 Sending contextual continuation to main chat...")
    
    ; Switch to main chat
    SwitchToMainChat()
    Sleep 500
    
    ; Clear input and send continuation prompt
    Send "^a"
    Sleep 100
    Send "{Delete}"
    Sleep 100
    
    ; Send the contextual continuation prompt
    A_Clipboard := analysis["continuationPrompt"]
    Send "^v"
    Sleep 500
    Send "{Enter}"
    
    ShowDebugTip("✅ Contextual continuation sent - AI should now continue intelligently")
}

; --- Configuration ---
global LogFile := A_ScriptDir "\ahk_log.txt"
FileDelete(LogFile) ; Clear log on each run
Log("Script started. Press F9 to toggle the assistant.")

; --- Functions ---
ToggleAssistant() {
    static Active := false
    Active := !Active
    if (Active) {
        Log("Assistant Activated.")
        SetTimer(ShowAcceptReject, 2000)
    } else {
        Log("Assistant Deactivated.")
        SetTimer(ShowAcceptReject, "Off")
        try {
            CoordMode "Mouse", "Screen"
            WinGetPos(&X, &Y, &W, &H, "A")
            ToolTip
        } catch as e {
            Log("Error disabling tooltip: " e.Message)
        }
    }
}

ShowAcceptReject() {
    try {
        CoordMode "Mouse", "Screen"
        WinGetPos(&X, &Y, &W, &H, "A")
        ToolTip("F6 to Accept | F7 to Reject", W - 200, H - 40)
    } catch as e {
        Log("Error in ShowAcceptReject: " e.Message)
    }
}

Accept() {
    Log("F6 Pressed: Accepting.")
    ClickAcceptButton()
}

Reject() {
    Log("F7 Pressed: Rejecting.")
    ClickRejectButton()
}

Log(message) {
    try {
        FileAppend(Format("[{1}] {2}`n", A_YYYY "-" A_MM "-" A_DD " " A_Hour ":" A_Min ":" A_Sec, message), LogFile)
    } catch as e {
        ; If logging fails, we can't do much. Maybe a tooltip?
        ToolTip("FATAL: Could not write to log file!")
    }
}

; New function to detect existing conversation
CheckForExistingConversation() {
    ShowDebugTip("🔍 Checking left window for existing conversation...")
    
    ; Focus left window
    MouseMove A_ScreenWidth * 0.25, A_ScreenHeight * 0.5
    Click
    Sleep 500
    
    ; Try to detect if there's already conversation content
    ; Look for common conversation indicators
    Send "^a"  ; Select all
    Sleep 300
    Send "^c"  ; Copy
    Sleep 300
    Send "{Escape}"  ; Clear selection
    
    conversationContent := A_Clipboard
    
    ; Check for indicators of active conversation
    hasConversation := false
    
    if (StrLen(conversationContent) > 100) {  ; Substantial content exists
        hasConversation := true
        ShowDebugTip("📝 Substantial content detected (" . StrLen(conversationContent) . " chars)")
    }
    
    ; Look for common conversation patterns
    if (InStr(conversationContent, "I'll") || InStr(conversationContent, "Let me") || 
        InStr(conversationContent, "Here's") || InStr(conversationContent, "I can") ||
        InStr(conversationContent, "```") || InStr(conversationContent, "function") ||
        InStr(conversationContent, "const ") || InStr(conversationContent, "import ")) {
        hasConversation := true
        ShowDebugTip("💬 Conversation patterns detected")
    }
    
    ; Check right window too
    ShowDebugTip("🔍 Checking right window for existing conversation...")
    MouseMove A_ScreenWidth * 0.75, A_ScreenHeight * 0.5
    Click
    Sleep 500
    
    Send "^a"
    Sleep 300
    Send "^c"
    Sleep 300
    Send "{Escape}"
    
    rightContent := A_Clipboard
    
    if (StrLen(rightContent) > 100) {
        hasConversation := true
        ShowDebugTip("📝 Right window also has content (" . StrLen(rightContent) . " chars)")
    }
    
    ; Clear clipboard to avoid confusion
    A_Clipboard := ""
    
    return hasConversation
}
