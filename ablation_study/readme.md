# Variations
- *20% Column Sampling (20\% Subsample)*. In this variant, we follow the experiment setting in FlashProfile~\cite{padhi2018flashprofile} and sample 20\% of the records in the \textbf{column sampling} process for pattern generation. }
    \item \qql{\textbf{Static $r_{cov}$ ($r_{cov}$=0.95)}. In this variant, we remove the \textbf{$r_{cov}$ estimation} component and use the default $r_{cov}=0.95$ for pattern inference.}
    \item \qql{\textbf{Full Match Template Generation($r_{EM}$=1)}. In this variant, we set $r_{EM}=1$ in the \textbf{constrained template generation} constraint to exactly match every record into their corresponding templates.}
    \item \qql{\textbf{Static Pattern Selection Threshold (SPST)}. In this variant, we use a static selection threshold instead of K-Means clustering in the \textbf{pattern selection} process: patterns with a frequency larger than 0.01 are selected. }
    \item \qql{\textbf{No Pattern Selection (NPS)}. In this variant, we remove the \textbf{pattern selection}  process and accept all the generated patterns. }
\end{itemize}
