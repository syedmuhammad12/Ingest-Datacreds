<?xml version="1.0" encoding="UTF-8"?>
<!--
		Conversion Style-Sheet (Upgrade - B.2 Part)

		Version:		0.9
		Date:			21/06/2011
		Status:		Step 4
		Author:		Laurent DESQUEPER (EU)

		Version:		1.0
		Date:			20/10/2015
		Status:			Draft
		Author:			Nick Halsey (EU)
		Amendment:	Addition of ICH CodeSystemVersion and EU specific data fields
-->
<xsl:stylesheet version="1.0" 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:hl7-org:v3" xmlns:mif="urn:hl7-org:v3/mif">

	<!-- Reaction : 
	E2B(R2): element "reaction"
	E2B(R3): element "primaryRole"
	-->
	<xsl:template match="reaction">
		<subjectOf2 typeCode="SBJ">
			<observation moodCode="EVN" classCode="OBS">
				<!-- internal reaction id -->
				<id root="RID{position()}"/>
				<code code="{$Reaction}" codeSystem="{$oidObservationCode}"/>
				<!-- B.2.i.3, 4, 5 Start, End and Duration of Reaction/Event -->
				<xsl:if test="string-length(reactionstartdate) > 0 or string-length(reactionenddate) > 0 or string-length(reactionduration) > 0">
					<xsl:choose>
						<xsl:when test="string-length(reactionstartdate) = 0 or string-length(reactionenddate) = 0 or string-length(reactionduration) = 0">
							<effectiveTime xsi:type="IVL_TS">
								<xsl:if test="string-length(reactionstartdate) > 0">
									<low value="{reactionstartdate}"/>
								</xsl:if>
								<xsl:if test="string-length(reactionduration) > 0 and (string-length(reactionstartdate) = 0 or string-length(reactionenddate) = 0)">
									<width value="{reactionduration}">
										<xsl:attribute name="unit">
											<xsl:call-template name="getMapping">
												<xsl:with-param name="type">UCUM</xsl:with-param>
												<xsl:with-param name="code" select="reactiondurationunit"/>
											</xsl:call-template>
										</xsl:attribute>
									</width>
								</xsl:if>
								<xsl:if test="string-length(reactionenddate) > 0">
									<high value="{reactionenddate}"/>
								</xsl:if>
							</effectiveTime>
						</xsl:when>
						<xsl:when test="string-length(reactionstartdate) > 0 and string-length(reactionenddate) > 0 and string-length(reactionduration) > 0">
						<effectiveTime xsi:type="SXPR_TS">
							<comp xsi:type="IVL_TS">
								<low value="{reactionstartdate}"/>
								<high value="{reactionenddate}"/>
							</comp>
							<comp xsi:type="IVL_TS" operator="A">
								<width value="{reactionduration}">
										<xsl:attribute name="unit">
											<xsl:call-template name="getMapping">
												<xsl:with-param name="type">UCUM</xsl:with-param>
												<xsl:with-param name="code" select="reactiondurationunit"/>
											</xsl:call-template>
										</xsl:attribute>
									</width>
							</comp>
						</effectiveTime>
						</xsl:when>
						<xsl:otherwise>
							<effectiveTime xsi:type="IVL_TS">
								<low value="{reactionstartdate}"/>
								<high value="{reactionenddate}"/>
							</effectiveTime>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:if>
				<!-- B.2.i.0, 1 Reaction/Event as Reported by Primary Source and in MedDRA terminology -->
				<xsl:if test="string-length(reactionmeddrallt) > 0 or string-length(primarysourcereaction) > 0">
					<value xsi:type="CE">
						<xsl:if test="string-length(reactionmeddrallt) > 0">
							<xsl:attribute name="codeSystem"><xsl:value-of select="$oidMedDRA"/></xsl:attribute>
							<xsl:attribute name="code"><xsl:value-of select="reactionmeddrallt"/></xsl:attribute>
						</xsl:if>
						<xsl:if test="string-length(reactionmeddraversionllt) > 0">
							<xsl:attribute name="codeSystemVersion"><xsl:value-of select="reactionmeddraversionllt"/></xsl:attribute>
						</xsl:if>
						<xsl:if test="string-length(primarysourcereaction) > 0">
							<originalText><xsl:value-of select="primarysourcereaction"/></originalText>
						</xsl:if>
					</value>
				</xsl:if>
				<!-- B.2.i Identification of the Country where the Reaction Occurred -->
				<xsl:if test="string-length(../../occurcountry) > 0">
					<location typeCode="LOC">
						<locatedEntity classCode="LOCE">
							<locatedPlace classCode="COUNTRY" determinerCode="INSTANCE">
								<code code="{../../occurcountry}" codeSystem="{$oidISOCountry}"/>
							</locatedPlace>
						</locatedEntity>
					</location>
				</xsl:if>
				<!-- B.2.i.2.1 Term Highlighted by Reporter -->
				<xsl:if test="string-length(termhighlighted) > 0">
					<outboundRelationship2 typeCode="PERT">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$TermHighlightedByReporter}" codeSystem="{$oidObservationCode}"/>
							<value xsi:type="CE" code="{termhighlighted}" codeSystem="{$oidTermHighlighted}" codeSystemVersion="{$oidTermHighlightedCSV}"/>
						</observation>
					</outboundRelationship2>
				</xsl:if>
				<!-- B.2.i.2.2 Seriousness Criteria at Event Level -->
				<outboundRelationship2 typeCode="PERT">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$ResultsInDeath}" codeSystem="{$oidObservationCode}"/>
						<xsl:choose>
							<xsl:when test="../../seriousnessdeath = 1">
								<value xsi:type="BL" value="true"/>
							</xsl:when>
							<xsl:otherwise>
								<value xsi:type="BL" nullFlavor="NI"/>
							</xsl:otherwise>
						</xsl:choose>
					</observation>
				</outboundRelationship2>
				<outboundRelationship2 typeCode="PERT">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$LifeThreatening}" codeSystem="{$oidObservationCode}"/>
						<xsl:choose>
							<xsl:when test="../../seriousnesslifethreatening = 1">
								<value xsi:type="BL" value="true"/>
							</xsl:when>
							<xsl:otherwise>
								<value xsi:type="BL" nullFlavor="NI"/>
							</xsl:otherwise>
						</xsl:choose>
					</observation>
				</outboundRelationship2>
				<outboundRelationship2 typeCode="PERT">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$CausedProlongedHospitalisation}" codeSystem="{$oidObservationCode}"/>
						<xsl:choose>
							<xsl:when test="../../seriousnesshospitalization = 1">
								<value xsi:type="BL" value="true"/>
							</xsl:when>
							<xsl:otherwise>
								<value xsi:type="BL" nullFlavor="NI"/>
							</xsl:otherwise>
						</xsl:choose>
					</observation>
				</outboundRelationship2>
				<outboundRelationship2 typeCode="PERT">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$DisablingIncapaciting}" codeSystem="{$oidObservationCode}"/>
						<xsl:choose>
							<xsl:when test="../../seriousnessdisabling = 1">
								<value xsi:type="BL" value="true"/>
							</xsl:when>
							<xsl:otherwise>
								<value xsi:type="BL" nullFlavor="NI"/>
							</xsl:otherwise>
						</xsl:choose>
					</observation>
				</outboundRelationship2>
				<outboundRelationship2 typeCode="PERT">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$CongenitalAnomalyBirthDefect}" codeSystem="{$oidObservationCode}"/>
						<xsl:choose>
							<xsl:when test="../../seriousnesscongenitalanomali = 1">
								<value xsi:type="BL" value="true"/>
							</xsl:when>
							<xsl:otherwise>
								<value xsi:type="BL" nullFlavor="NI"/>
							</xsl:otherwise>
						</xsl:choose>
					</observation>
				</outboundRelationship2>
				<outboundRelationship2 typeCode="PERT">
					<observation moodCode="EVN" classCode="OBS">
						<code code="{$OtherMedicallyImportantCondition}" codeSystem="{$oidObservationCode}"/>
						<xsl:choose>
							<xsl:when test="../../seriousnessother = 1">
								<value xsi:type="BL" value="true"/>
							</xsl:when>
							<xsl:otherwise>
								<value xsi:type="BL" nullFlavor="NI"/>
							</xsl:otherwise>
						</xsl:choose>
					</observation>
				</outboundRelationship2>
				<!-- B.2.i.8 Outcome of the Reaction -->
				<xsl:if test="string-length(reactionoutcome)>0">
					<outboundRelationship2 typeCode="PERT">
						<observation moodCode="EVN" classCode="OBS">
							<code code="{$Outcome}" codeSystem="{$oidObservationCode}"/>
							<xsl:choose>
								<xsl:when test="reactionoutcome = 6"><value xsi:type="CE" code="0" codeSystem="{$oidOutcome}" codeSystemVersion="{$oidOutcomeCSV}"/></xsl:when>
								<xsl:otherwise>
									<value xsi:type="CE" code="{reactionoutcome}" codeSystem="{$oidOutcome}" codeSystemVersion="{$oidOutcomeCSV}"/>
								</xsl:otherwise>
							</xsl:choose>
						</observation>
					</outboundRelationship2>
				</xsl:if>
			</observation>
		</subjectOf2>
	</xsl:template>
</xsl:stylesheet>
