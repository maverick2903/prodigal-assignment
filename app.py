import streamlit as st
import pandas as pd
import json
from task1_profanity.regex_detector import ProfanityRegexDetector
from task1_profanity.llm_detector import ProfanityLLMDetector
from task2_privacy.regex_detector import ComplianceRegexDetector
from task2_privacy.llm_detector import ComplianceLLMDetector
from task3_metrics.call_quality import CallQualityAnalyzer
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.title("📞 Call Analysis Tool")

uploaded_file = st.file_uploader("Upload a conversation JSON file", type=["json"])
if uploaded_file:
    conversation = json.load(uploaded_file)

    tab1, tab2 = st.tabs(["🗣️ Entity Detection", "📊 Call Quality Metrics"])

    with tab1:
        st.header("Entity Detection")
        approach = st.selectbox("Select Approach", ["Pattern Matching", "LLM"])
        entity = st.selectbox("Select Entity to Analyze", ["Profanity Detection", "Privacy and Compliance Violation"])

        # Map selection to detector
        def run_detector(entity: str, approach: str, convo):
            if entity == "Profanity Detection":
                if approach == "Pattern Matching":
                    detector = ProfanityRegexDetector()
                else:
                    detector = ProfanityLLMDetector()
                result = detector.analyze_conversation(convo)
                return result.get("agent_profanity"), result.get("borrower_profanity")

            elif entity == "Privacy and Compliance Violation":
                if approach == "Pattern Matching":
                    detector = ComplianceRegexDetector()
                else:
                    detector = ComplianceLLMDetector()
                result = detector.analyze_conversation(convo)
                return result.get("privacy_violation"), None

        # Run the selected analysis
        with st.spinner("Analyzing..."):
            flag1, flag2 = run_detector(entity, approach, conversation)

        # Show results
        st.success("Analysis complete.")
        if entity == "Profanity Detection":
            st.write("### 🔍 Detection Results:")
            st.write(f"- Agent used profanity: {'✅ Yes' if flag1 else '❌ No'}")
            st.write(f"- Borrower used profanity: {'✅ Yes' if flag2 else '❌ No'}")
        elif entity == "Privacy and Compliance Violation":
            st.write("### 🔐 Compliance Result:")
            st.write(f"- Privacy Violation Detected: {'⚠️ Yes' if flag1 else '✅ No'}")


    with tab2:
        st.header("Call Quality Metrics")

        analyzer = CallQualityAnalyzer()
        result = analyzer.analyze(conversation)

        # Compute true total percentages
        total = result['total_duration']
        silence = result['silence_duration']
        speaking = result['speaking_duration']
        overtalk = result['overtalk_duration']
        solo_speaking = speaking - overtalk

        # Percentages
        silence_pct = (silence / total) * 100
        speaking_pct = (solo_speaking / total) * 100
        overtalk_pct = (overtalk / total) * 100
        overtalk_within_speaking = (overtalk / speaking) * 100 if speaking > 0 else 0

        # Layout
        st.markdown("### 🔍 Summary")
        st.markdown(
            f"""
            - 🕒 **Total Call Duration:** `{total:.2f}` seconds  
            - 🔇 **Silence:** `{silence_pct:.2f}%` of total call  
            - 🗣️ **Speaking:** `{speaking_pct + overtalk_pct:.2f}%`  
                - 🔁 **Overtalk:** `{overtalk_pct:.2f}%` of total  
                - 📊 **Overtalk Share of Speaking:** `{overtalk_within_speaking:.2f}%`
            """
        )

        # Pie Chart
        st.markdown("### 📊 Duration Distribution")
        labels, sizes, colors = [], [], []

        if silence_pct > 0:
            labels.append('Silence')
            sizes.append(silence_pct)
            colors.append('#ffc107')

        if speaking_pct > 0:
            labels.append('Speaking (Solo)')
            sizes.append(speaking_pct)
            colors.append('#4caf50')

        if overtalk_pct > 0:
            labels.append('Overtalk')
            sizes.append(overtalk_pct)
            colors.append('#f44336')

        if sizes:
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.info("No segments to display in pie chart.")

        def create_conversation_timeline(conversation):
            # Find the total duration of the call
            total_duration = max([seg["etime"] for seg in conversation])
            
            # Create separate entries for each speaker
            agent_segments = []
            customer_segments = []
            silence_segments = []
            
            # Track last end time to detect silences
            last_end_time = 0
            
            for i, seg in enumerate(conversation):
                # Check for silence before this segment
                if seg["stime"] > last_end_time + 0.5:  # Using 0.5s threshold for silence
                    silence_segments.append({
                        'Start': last_end_time,
                        'End': seg["stime"],
                    })
                
                # Update last end time if this segment ends later
                last_end_time = max(last_end_time, seg["etime"])
                
                # Add to appropriate speaker list
                if seg["speaker"] == "Agent":
                    agent_segments.append({
                        'Start': seg["stime"],
                        'End': seg["etime"],
                        'Text': seg["text"]
                    })
                else:  # Customer
                    customer_segments.append({
                        'Start': seg["stime"],
                        'End': seg["etime"],
                        'Text': seg["text"]
                    })
            
            # Create the visualization
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Define colors
            agent_color = "#4682B4"  # Steel Blue
            customer_color = "#6B8E23"  # Olive Drab
            overlap_color = "#FF6347"  # Tomato
            silence_color = "#DCDCDC"  # Light Gray
            
            # Plot silences first (in background)
            for segment in silence_segments:
                ax.barh(y=0, width=segment['End'] - segment['Start'], 
                        left=segment['Start'], height=2, color=silence_color, alpha=0.3)
            
            # Plot Agent speech (top row)
            for segment in agent_segments:
                # Check for overlaps with customer
                is_overlapping = False
                for cust_seg in customer_segments:
                    if (segment['Start'] < cust_seg['End'] and 
                        segment['End'] > cust_seg['Start']):
                        is_overlapping = True
                        break
                
                color = overlap_color if is_overlapping else agent_color
                bar = ax.barh(y=1, width=segment['End'] - segment['Start'], 
                            left=segment['Start'], height=0.8, color=color)
                
                # Add text annotation if there's enough room
                if segment['End'] - segment['Start'] > 3:
                    short_text = segment['Text'][:20] + "..." if len(segment['Text']) > 20 else segment['Text']
                    ax.text(segment['Start'] + 0.1, 1, short_text, va='center', fontsize=8, color='white')
            
            # Plot Customer speech (bottom row)
            for segment in customer_segments:
                # Check for overlaps with agent
                is_overlapping = False
                for agent_seg in agent_segments:
                    if (segment['Start'] < agent_seg['End'] and 
                        segment['End'] > agent_seg['Start']):
                        is_overlapping = True
                        break
                
                color = overlap_color if is_overlapping else customer_color
                bar = ax.barh(y=0, width=segment['End'] - segment['Start'], 
                            left=segment['Start'], height=0.8, color=color)
                
                # Add text annotation if there's enough room
                if segment['End'] - segment['Start'] > 3:
                    short_text = segment['Text'][:20] + "..." if len(segment['Text']) > 20 else segment['Text']
                    ax.text(segment['Start'] + 0.1, 0, short_text, va='center', fontsize=8, color='white')
            
            # Set y-axis ticks and labels
            ax.set_yticks([0, 1])
            ax.set_yticklabels(['Customer', 'Agent'])
            
            # Set x-axis and title
            ax.set_xlim(0, total_duration)
            ax.set_xlabel("Time (seconds)")
            ax.set_title("Conversation Timeline")
            
            # Add a grid for better time reference
            ax.grid(axis='x', linestyle='--', alpha=0.6)
            
            # Add legend
            legend_patches = [
                mpatches.Patch(color=agent_color, label='Agent Speaking'),
                mpatches.Patch(color=customer_color, label='Customer Speaking'),
                mpatches.Patch(color=overlap_color, label='Overlapping Speech'),
                mpatches.Patch(color=silence_color, label='Silence', alpha=0.3),
            ]
            ax.legend(handles=legend_patches, loc='upper right')
            
            return fig

        # In a Streamlit app, you would use it like:
        st.markdown("### 🕓 Conversation Timeline")
        fig = create_conversation_timeline(conversation)
        st.pyplot(fig)

        # Additional statistics
        def calculate_conversation_stats(conversation):
            total_duration = max([seg["etime"] for seg in conversation])
            
            # Calculate speaker stats
            agent_time = sum([seg["etime"] - seg["stime"] for seg in conversation if seg["speaker"] == "Agent"])
            customer_time = sum([seg["etime"] - seg["stime"] for seg in conversation if seg["speaker"] == "Customer"])
            
            # Calculate overlaps
            overlaps = []
            for i, seg1 in enumerate(conversation):
                for j, seg2 in enumerate(conversation[i+1:], i+1):
                    if seg1["speaker"] != seg2["speaker"]:
                        # Check if they overlap
                        if seg1["stime"] < seg2["etime"] and seg1["etime"] > seg2["stime"]:
                            overlap_start = max(seg1["stime"], seg2["stime"])
                            overlap_end = min(seg1["etime"], seg2["etime"])
                            overlaps.append({
                                "start": overlap_start,
                                "end": overlap_end,
                                "duration": overlap_end - overlap_start
                            })
            
            total_overlap_time = sum([o["duration"] for o in overlaps])
            
            # Calculate silence
            silence_time = 0
            last_end = 0
            for seg in sorted(conversation, key=lambda x: x["stime"]):
                if seg["stime"] > last_end + 0.5:  # 0.5s threshold
                    silence_time += seg["stime"] - last_end
                last_end = max(last_end, seg["etime"])
            
            # Create a table of stats
            stats = {
                "Agent Speaking Time": f"{agent_time:.1f}s ({agent_time/total_duration*100:.1f}%)",
                "Customer Speaking Time": f"{customer_time:.1f}s ({customer_time/total_duration*100:.1f}%)",
                "Overlap Time": f"{total_overlap_time:.1f}s ({total_overlap_time/total_duration*100:.1f}%)",
                "Silence Time": f"{silence_time:.1f}s ({silence_time/total_duration*100:.1f}%)",
                "Total Call Duration": f"{total_duration:.1f}s"
            }
            
            # Display as a Streamlit metric grid
            col1, col2, col3 = st.columns(3)
            col1.metric("Agent Speaking", f"{agent_time:.1f}s", f"{agent_time/total_duration*100:.1f}%")
            col2.metric("Customer Speaking", f"{customer_time:.1f}s", f"{customer_time/total_duration*100:.1f}%")
            col3.metric("Total Duration", f"{total_duration:.1f}s")
            
            col1, col2 = st.columns(2)
            col1.metric("Overlapping Speech", f"{total_overlap_time:.1f}s", f"{total_overlap_time/total_duration*100:.1f}%")
            col2.metric("Silence Time", f"{silence_time:.1f}s", f"{silence_time/total_duration*100:.1f}%")
            
            return stats

        # Call the stats function
        calculate_conversation_stats(conversation)

