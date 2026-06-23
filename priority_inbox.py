from datetime import datetime

notifications = [
    {
        "ID": "e1496bbd-ec98-41d4-b890-5ad29a5e889c",
        "Type": "Event",
        "Message": "traditional-day",
        "Timestamp": "2026-06-22 11:35:12"
    },
    {
        "ID": "df1eebba-ba4c-4a71-848b-486d8aa9be7d",
        "Type": "Result",
        "Message": "external",
        "Timestamp": "2026-06-22 07:34:59"
    },
    {
        "ID": "afa12941-36e5-43ca-886c-33c9fc91ba62",
        "Type": "Event",
        "Message": "traditional-day",
        "Timestamp": "2026-06-23 05:04:46"
    },
    {
        "ID": "a9c5fd8c-310b-4db9-96c0-a5fb217065fb",
        "Type": "Event",
        "Message": "farewell",
        "Timestamp": "2026-06-22 19:04:33"
    },
    {
        "ID": "54276c97-b115-4666-8116-ff2262585296",
        "Type": "Result",
        "Message": "project-review",
        "Timestamp": "2026-06-22 17:34:20"
    },
    {
        "ID": "68b6448d-f666-418b-b8cf-1f25f9630525",
        "Type": "Placement",
        "Message": "Broadcom Inc. hiring",
        "Timestamp": "2026-06-22 16:33:54"
    },
    {
        "ID": "45076c9c-945a-439d-8bd7-449cf87e9d31",
        "Type": "Result",
        "Message": "end-sem",
        "Timestamp": "2026-06-23 04:33:41"
    },
    {
        "ID": "1e366b42-936a-4ead-beb9-c772c220f5f7",
        "Type": "Result",
        "Message": "mid-sem",
        "Timestamp": "2026-06-23 04:03:28"
    },
    {
        "ID": "fde66877-e39d-4029-9219-b668a59e5cd5",
        "Type": "Placement",
        "Message": "Visa Inc. hiring",
        "Timestamp": "2026-06-22 20:03:15"
    },
    {
        "ID": "7d957eb5-3b79-4846-8a1a-64b651254b4f",
        "Type": "Placement",
        "Message": "Advanced Micro Devices Inc. hiring",
        "Timestamp": "2026-06-22 17:33:02"
    },
    {
        "ID": "54e96dd6-aa6f-446e-b691-008f0c40b3a8",
        "Type": "Placement",
        "Message": "Berkshire Hathaway Inc. hiring",
        "Timestamp": "2026-06-22 20:32:49"
    },
    {
        "ID": "9c653dae-dc22-4970-9d88-ee3157a8eb5f",
        "Type": "Placement",
        "Message": "Nvidia Corporation hiring",
        "Timestamp": "2026-06-22 23:02:36"
    },
    {
        "ID": "d4800182-7ac9-4804-b034-315be0589989",
        "Type": "Placement",
        "Message": "Marvell Technology Inc. hiring",
        "Timestamp": "2026-06-23 06:02:23"
    },
    {
        "ID": "e1aafbd1-1eac-4d1e-98bd-ad4f1d151409",
        "Type": "Event",
        "Message": "traditional-day",
        "Timestamp": "2026-06-23 04:32:10"
    },
    {
        "ID": "f632d5e8-fe13-4e05-9611-afed0c08ab94",
        "Type": "Event",
        "Message": "induction",
        "Timestamp": "2026-06-22 12:01:57"
    },
    {
        "ID": "a1b8661d-553c-4de2-a224-101606c6822d",
        "Type": "Event",
        "Message": "farewell",
        "Timestamp": "2026-06-22 10:01:44"
    },
    {
        "ID": "a8ab7182-1d20-4e22-88bf-0584ea878aaa",
        "Type": "Placement",
        "Message": "Marriott International Inc. hiring",
        "Timestamp": "2026-06-22 21:01:31"
    },
    {
        "ID": "ccbbd7f5-8af3-4e1e-884b-655a642ca8a1",
        "Type": "Result",
        "Message": "end-sem",
        "Timestamp": "2026-06-22 13:31:18"
    },
    {
        "ID": "f488ce5b-67df-41f0-a4f4-2d541b474ef0",
        "Type": "Result",
        "Message": "mid-sem",
        "Timestamp": "2026-06-22 07:01:05"
    }
]

weights = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}

for notification in notifications:
    notification["priority"] = weights[notification["Type"]]
    notification["parsed_time"] = datetime.strptime(
        notification["Timestamp"],
        "%Y-%m-%d %H:%M:%S"
    )

top_10 = sorted(
    notifications,
    key=lambda x: (x["priority"], x["parsed_time"]),
    reverse=True
)[:10]

print("TOP 10 PRIORITY NOTIFICATIONS\n")

for i, n in enumerate(top_10, start=1):
    print(
        f"{i}. [{n['Type']}] "
        f"{n['Message']} | "
        f"{n['Timestamp']}"
    )