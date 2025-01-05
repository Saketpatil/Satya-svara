import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";
import { promisify } from "util";
import { exec as execCallback } from "child_process";

const exec = promisify(execCallback);

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const file = formData.get("file");

  if (!file || !(file instanceof Blob)) {
    console.error("Invalid file upload");
    return NextResponse.json({ error: "Invalid file upload" }, { status: 400 });
  }

  const buffer = Buffer.from(await file.arrayBuffer());
  const filePath = path.join(
    path.resolve(process.cwd(), "python"),
    "uploads",
    `${Date.now()}-${file.name}`
  );

  try {
    await fs.mkdir(path.dirname(filePath), { recursive: true });
    await fs.writeFile(filePath, buffer);

    try {
      const { stdout } = await exec(`python python/analyze.py "${filePath}"`, {
        encoding: "utf-8",
      });

      const parsedJson = JSON.parse(stdout.trim().split("\n").pop()!);
      console.log("Parsed JSON:", parsedJson);
      return NextResponse.json({
        message: "File uploaded and analyzed successfully",
        result: parsedJson,
      });
    } catch (error) {
      console.error("Error during subprocess execution:", error);
      return NextResponse.json(
        { error: "Error analyzing audio" },
        { status: 500 }
      );
    } finally {
      fs.unlink(filePath);
    }
  } catch (error) {
    console.error("Error saving file:", error);
    return NextResponse.json({ error: "Error saving file" }, { status: 500 });
  }
}
