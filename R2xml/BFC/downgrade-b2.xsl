<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Downgrade - B.2 Part)
		Input : 			ICSR File compliant with E2B(R3)
		Output : 		ICSR File compliant with E2B(R2)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 2
		Author:		Laurent DESQUEPER (EU)

		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of conversions for EU specific data fields
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xmlns:hl7="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif"  exclude-result-prefixes="hl7 xsi xsl fo mif">
	
	<!--	B.2. Reaction(s)/Event(s) -->
	<xsl:template match="hl7:observation" mode="reaction">
		<xsl:variable name="reactionID" select="hl7:id/@root"/>
		<reaction>
			<primarysourcereaction>
				<xsl:call-template name="truncate">
					<xsl:with-param name="string">
						<xsl:choose>
							<xsl:when test="string-length(hl7:outboundRelationship2/hl7:observation[hl7:code/@code = $ReactionForTranslation and hl7:code/@codeSystem=$oidObservationCode]/hl7:value) > 0">
								<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code = $ReactionForTranslation and hl7:code/@codeSystem=$oidObservationCode]/hl7:value"/>
							</xsl:when>
							<xsl:otherwise><xsl:value-of select="hl7:value/hl7:originalText"/></xsl:otherwise>
						</xsl:choose>
					</xsl:with-param>
					<xsl:with-param name="string-length">200</xsl:with-param>
				</xsl:call-template>
			</primarysourcereaction>
			<reactionmeddraversionllt>
				<xsl:value-of select="hl7:value/@codeSystemVersion"/>
			</reactionmeddraversionllt>
			<reactionmeddrallt>
				<xsl:value-of select="hl7:value/@code"/>
			</reactionmeddrallt>
			<!-- B.2.i.2.1 Term highlighted  -->
			<xsl:call-template name="TermHighlighted">
				<xsl:with-param name="reactionID">
					<xsl:value-of select="$reactionID"/>
				</xsl:with-param>
			</xsl:call-template>
			<xsl:if test="count(hl7:effectiveTime/hl7:comp) > 0">
				<xsl:if test="count(hl7:effectiveTime/hl7:comp[1]/hl7:low) > 0">
					<xsl:call-template name="convertDate">
						<xsl:with-param name="elementName">reactionstartdate</xsl:with-param>
						<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:comp[1]/hl7:low/@value"/>
						<xsl:with-param name="min-format">CCYY</xsl:with-param>
						<xsl:with-param name="max-format">CCYYMMDDHHMM</xsl:with-param>
					</xsl:call-template>
				</xsl:if>
				<xsl:if test="count(hl7:effectiveTime/hl7:comp[1]/hl7:high) > 0">
					<xsl:call-template name="convertDate">
						<xsl:with-param name="elementName">reactionenddate</xsl:with-param>
						<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:comp[1]/hl7:high/@value"/>
						<xsl:with-param name="min-format">CCYY</xsl:with-param>
						<xsl:with-param name="max-format">CCYYMMDDHHMM</xsl:with-param>
					</xsl:call-template>
				</xsl:if>
				<xsl:if test="count(hl7:effectiveTime/hl7:comp[2]/hl7:width) > 0">
					<reactionduration>
						<xsl:value-of select="hl7:effectiveTime/hl7:comp[2]/hl7:width/@value"/>
					</reactionduration>
					<reactiondurationunit>
						<xsl:call-template name="getMapping">
							<xsl:with-param name="type">UCUM</xsl:with-param>
							<xsl:with-param name="code" select="hl7:effectiveTime/hl7:comp[2]/hl7:width/@unit"/>
						</xsl:call-template>
					</reactiondurationunit>
				</xsl:if>
			</xsl:if>
			<xsl:if test="count(hl7:effectiveTime/hl7:low) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">reactionstartdate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:low/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDDHHMM</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<xsl:if test="count(hl7:effectiveTime/hl7:high) > 0">
				<xsl:call-template name="convertDate">
					<xsl:with-param name="elementName">reactionenddate</xsl:with-param>
					<xsl:with-param name="date-value" select="hl7:effectiveTime/hl7:high/@value"/>
					<xsl:with-param name="min-format">CCYY</xsl:with-param>
					<xsl:with-param name="max-format">CCYYMMDDHHMM</xsl:with-param>
				</xsl:call-template>
			</xsl:if>
			<xsl:if test="count(hl7:effectiveTime/hl7:width) > 0">
				<reactionduration>
					<xsl:value-of select="hl7:effectiveTime/hl7:width/@value"/>
				</reactionduration>
				<reactiondurationunit>
					<xsl:call-template name="getMapping">
						<xsl:with-param name="type">UCUM</xsl:with-param>
						<xsl:with-param name="code" select="hl7:effectiveTime/hl7:width/@unit"/>
					</xsl:call-template>
				</reactiondurationunit>
			</xsl:if>
			<xsl:apply-templates select="../../hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugInformation]/hl7:component/hl7:substanceAdministration/hl7:sourceOf1[@typeCode='SAS' and hl7:actReference/hl7:id/@root = $reactionID]" mode="SAS"/>
			<xsl:apply-templates select="../../hl7:subjectOf2/hl7:organizer[hl7:code/@code=$DrugInformation]/hl7:component/hl7:substanceAdministration/hl7:sourceOf1[@typeCode='SAE' and hl7:actReference/hl7:id/@root = $reactionID]" mode="SAE"/>
			<reactionoutcome>
				<xsl:choose>
					<xsl:when test="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Outcome and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code = 0">6</xsl:when>
					<xsl:otherwise><xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$Outcome and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code"/></xsl:otherwise>
				</xsl:choose>
			</reactionoutcome>
		</reaction>
	</xsl:template>
	
	<!-- B.2.i.2.1 Term Highlighted -->
	<xsl:template name="TermHighlighted">
		<termhighlighted>
			<xsl:value-of select="hl7:outboundRelationship2/hl7:observation[hl7:code/@code=$TermHighlightedByReporter and hl7:code/@codeSystem=$oidObservationCode]/hl7:value/@code"/>
		</termhighlighted>
	</xsl:template>
	
	<!-- B.2.i.7.1 Reaction first time -->
	<xsl:template match="hl7:sourceOf1" mode="SAS">
		<reactionfirsttime>
			<xsl:value-of select="hl7:pauseQuantity/@value" />
		</reactionfirsttime>
		<reactionfirsttimeunit>
			<xsl:call-template name="getMapping">
				<xsl:with-param name="type">UCUM</xsl:with-param>
				<xsl:with-param name="code" select="hl7:pauseQuantity/@unit"/>
			</xsl:call-template>
		</reactionfirsttimeunit>
	</xsl:template>
	
	<!-- B.2.i.7.2 Reaction last time -->
	<xsl:template match="hl7:sourceOf1" mode="SAE">
		<reactionlasttime>
			<xsl:value-of select="hl7:pauseQuantity/@value" />
		</reactionlasttime>
		<reactionlasttimeunit>
			<xsl:call-template name="getMapping">
				<xsl:with-param name="type">UCUM</xsl:with-param>
				<xsl:with-param name="code" select="hl7:pauseQuantity/@unit"/>
			</xsl:call-template>
		</reactionlasttimeunit>
	</xsl:template>
	
</xsl:stylesheet>
